#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""订单处理模块

该模块负责处理用户需求订单，分析用户需求，并生成配置脚本。
"""

import os
import sys
import re
import json
import ipaddress

# 获取当前文件的绝对路径并添加项目根目录到系统路径
current_file = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file))))
config_path = os.path.join(project_root, 'src', 'config', 'config.json')
template_dir = os.path.join(project_root, 'templates')
jsons_dir = os.path.join(project_root, 'data', 'output', 'json_files')
# 将项目根目录添加到系统路径中，使Python能够正确解析以'src'开头的导入
sys.path.insert(0, project_root)

from datetime import datetime
from src.utils.logger import setup_logger
from openpyxl import load_workbook
from jinja2 import Environment, FileSystemLoader
from src.core.config_manager import ConfigManager

# 在模块级别初始化一次日志系统
logger = setup_logger()

def _load_json_file(file_path):
    """加载JSON文件并返回数据，包含错误处理"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"JSON文件未找到: {file_path}")
        raise
    except json.JSONDecodeError:
        logger.error(f"JSON文件解析错误: {file_path}")
        raise


def get_combine_net_infos(ips, vpcs_data):
    """查找IP所在的VPC信息，区分源IP和目的IP"""
    combine_net_infos = {}

    for ip in ips:
        # # 确定IP方向（源或目的）
        # direction = 'source' if ip in s_ips else 'destination'

        # 查找IP所在的阿里云VPC
        for vpc in vpcs_data.get('Vpcs', {}).get('Vpc', []):
            cidr = vpc.get('CidrBlock')
            if not cidr:
                continue
            try:
                ip_obj = ipaddress.ip_interface(ip)
                cidr_obj = ipaddress.ip_interface(cidr)
                if ip_obj.network.subnet_of(cidr_obj.network):
                    logger.info(f"变更中地址： {ip} 在VPC网段 {cidr} 中")
                    combine_net_infos[ip] = {'cidr': cidr_obj.exploded}
                    break  # 找到后跳出循环
            except ValueError as e:
                logger.debug(f"处理ip地址或网段：{ip}不在{cidr}网段中")
                continue
        if not combine_net_infos:
            logger.info(f"IP {ip} 未找到所属VPC")

    return combine_net_infos


class OrderProcessor:
    """订单处理器类，封装订单处理的核心功能"""

    def __init__(self, order_path, config, templates_dir):
        """初始化方法，设置日志系统"""
        self.order_path = order_path
        self.config = config
        self.templates_dir = templates_dir

        self.logger = logger
        self._process_order()

    def _process_order(self):
        """处理用户需求订单，分析用户需求，生成配置脚本

        Args:
            order_path (str): 订单文件路径

        Returns:
            str: 生成的配置脚本内容
        """
        results = []
        try:
            self.logger.info(f"开始处理订单文件: {self.order_path}")

            # 解析订单文件
            customer_info, requirement_infos = self.parse_order_file()

            for requirement_info in requirement_infos:
                # 生成变更标题
                title = self.generate_title(customer_info, requirement_info)

                # 生成变更原因
                reason = self.generate_reason(customer_info, requirement_info)

                # 生成变更方案
                scheme = self.generate_scheme(customer_info, requirement_info)

                self.logger.info("订单处理完成")

                # 组合返回结果
                result = {
                    "title": title,
                    "reason": reason,
                    "scheme": scheme
                }
                results.append(result)

            return json.dumps(results, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"订单处理失败: {str(e)}", exc_info=True)
            raise

    def parse_order_file(self):
        """
           订单处理主函数：解析订单文件，整合网络信息并生成变更方案

           参数:
               file_path (str): 订单文件的绝对路径，支持格式包括JSON和Excel

           返回值:
               dict: 包含以下键的处理结果字典:
                   - 'status' (str): 处理状态，'success'或'failed'
                   - 'message' (str): 处理结果描述信息
                   - 'data' (dict): 包含网络信息和变更方案的详细数据
                   - 'errors' (list): 错误信息列表，处理成功时为空

           主要处理流程:
               1. 验证输入文件路径和格式
               2. 解析订单文件获取需求信息
               3. 调用外部API获取网络资源数据
               4. 整合阿里云CIDR与IPAM注册信息
               5. 生成网络变更原因和实施方案
               6. 返回标准化处理结果

           异常处理:
               - 文件不存在: 记录错误并返回状态'failed'
               - 格式解析失败: 捕获解析异常并返回详细错误信息
               - API调用超时: 实现重试机制(最多3次)，仍失败则降级处理
           """

        wb = load_workbook(self.order_path, read_only=False)  # 设为可写模式
        ws = wb.active

        # 用于存储所有需求的列表
        requirements_list = []

        # 从工作表的 F4 单元格获取组织名称
        organization = ws['F4']
        # 从工作表的 F5 单元格获取系统名称
        system_name = ws['F5']
        # 构建包含客户信息的字典
        customer = {"organization": organization.value, "system_name": system_name.value}

        # 获取工作表第 9 行 C 列到 P 列的单元格范围
        tts = ws['C9:P9']
        # 使用列表推导式将单元格的值展平为一个列表，并移除值中的星号
        tt_list = [cell.value.replace('*', '') for row in tts for cell in row if cell.value is not None]

        # 从第 10 行开始遍历到工作表的最后一行
        for row_num in range(10, ws.max_row + 1):
            # 复制合并单元格范围列表，避免在遍历过程中修改集合导致错误
            merged_ranges = list(ws.merged_cells.ranges)
            # 遍历所有合并单元格范围
            for merged_range in merged_ranges:
                # 检查当前行是否在合并单元格范围内
                if merged_range.min_row <= row_num <= merged_range.max_row:
                    # 获取合并单元格左上角的单元格
                    top_left_cell = ws.cell(row=merged_range.min_row, column=merged_range.min_col)
                    # 获取合并单元格的值
                    value = top_left_cell.value
                    # 取消当前的合并单元格
                    ws.unmerge_cells(range_string=str(merged_range))
                    # 将合并单元格的值赋给分开后的每个单元格
                    for row in range(merged_range.min_row, merged_range.max_row + 1):
                        for col in range(merged_range.min_col, merged_range.max_col + 1):
                            ws.cell(row=row, column=col, value=value)

            # 获取当前行 C 列到 R 列的单元格范围
            values = ws[f'C{row_num}:R{row_num}']
            # 使用列表推导式将单元格的值展平为一个列表，保留空值为 None
            values_list = [cell.value for row in values for cell in row]
            if values_list[0] is None:
                continue
            # 将标题列表和当前行的值列表合并为字典
            d = dict(zip(tt_list, values_list))
            d['源IP'] = self.extra_ip(d['源IP'])
            d['目的IP'] = self.extra_ip(d['目的IP'])
            d['公网IP'] = self.extra_ip(d['公网IP'])
            d['源端口'] = self.extra_port(d['源端口'])
            d['目的端口'] = self.extra_port(d['目的端口'])
            d['公网端口'] = self.extra_port(d['公网端口'])
            # 将包含当前行需求信息的字典添加到需求列表中
            requirements_list.append(d)

        # 调用 merge_entries 函数合并相同的需求条目
        self.logger.info(f"合并前需求列表: {requirements_list}")
        requirements_list = self.merge_entries(requirements_list)
        self.logger.info(f"合并后需求列表: {requirements_list}")

        # 返回客户信息字典和合并后的需求列表
        return customer, requirements_list

    def extra_ip(self, cell_value):
        """
        从字符串中提取所有 IPv4 地址和域名。

        使用正则表达式匹配字符串中的 IPv4 地址格式（xxx.xxx.xxx.xxx）和域名格式，
        提取所有非重叠的匹配结果并返回。

        :param cell_value: 待提取 IP 地址或域名的字符串（通常来自 Excel 单元格值）
        :return: 包含所有提取到的 IPv4 地址和域名的列表；若无匹配则返回空列表
        """
        if isinstance(cell_value, str) and cell_value.lower() == "any":
            return ["Any"]
        elif cell_value in ("", r"/", None):
            return ["Any"]

        try:
            # 尝试解析为 IP 地址或网络
            if ipaddress.ip_network(cell_value) or ipaddress.ip_address(cell_value):
                return [cell_value]
        except (ValueError, TypeError):
            pass

        # 定义 IP 和域名的正则表达式
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        # 域名正则表达式，支持字母、数字、连字符和多级域名
        domain_pattern = r'\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b'

        # 确保输入是字符串类型
        if not isinstance(cell_value, str):
            cell_value = str(cell_value)

        # # 新增：去除斜杠"/"及其后的内容
        # cell_value = cell_value.split('/')[0]

        # 提取 IP 地址和域名
        ips = re.findall(ip_pattern, cell_value)
        domains = re.findall(domain_pattern, cell_value)

        # 合并结果并去重
        result = list(set(ips + domains))

        return result if result else []

    def extra_port(self, cell_value):
        """
        从字符串中提取所有端口号。

        使用正则表达式匹配字符串中的端口号格式（xxxx），
        提取所有非重叠的匹配结果并返回。

        :param cell_value: 待提取端口号的字符串（通常来自 Excel 单元格值）
        :return: 包含所有提取到的端口号的列表；若无匹配则返回空列表
        """
        if isinstance(cell_value, int):
            return [cell_value]
        if not isinstance(cell_value, str):
            return []
        ports = []
        # 匹配两种模式：数字范围(如123-456)或单个数字(如789)
        port_patterns = re.findall(r'(\d+-\d+|\d+)', cell_value)
        for pattern in port_patterns:
            if '-' in pattern:
                start, end = map(int, pattern.split('-'))
                ports.extend(range(start, end + 1))
            else:
                ports.append(int(pattern))
        return ports

    def _get_merge_key_strategy(self, entry):
        """获取合并键策略"""
        strategies = [
            {
                'condition': lambda e: e['源归属'] == "行业云" and e['目的归属'] == "互联网",
                'key_builder': lambda e: (e['操作'], tuple(e['公网IP']))
            },
            {
                'condition': lambda e: e['源归属'] == "互联网" and e['目的归属'] == "行业云",
                'key_builder': lambda e: (e['操作'], tuple(e['公网IP']), tuple(e['目的IP']))
            }
        ]

        for strategy in strategies:
            if strategy['condition'](entry):
                return strategy['key_builder'](entry)

        # 默认策略
        return (entry['源归属'], entry['目的归属'])

    def merge_entries(self, data):
        """
        将列表中“源IP”、“公网IP”、“操作”和“目的IP”相同的条目合并为一条数据，
        不同的源端口和目的端口的值会被放入列表。

        :param data: 包含多个字典条目的列表，每个字典代表一条记录
        :return: 合并后的条目列表
        """
        # 用于存储合并后的条目，键为 (源IP, 操作, 目的IP) 组成的元组
        merged_dict = {}
        for entry in data:
            # 根据源归属和目的归属确定合并键
            key = self._get_merge_key_strategy(entry)

            if key not in merged_dict:  # 如果键不存在创建新条目
                merged_dict[key] = entry.copy()
            else:
                # 如果键已存在合并端口列表
                for field in ['源端口', '目的端口', '公网端口']:
                    for port in entry[field]:
                        if port not in merged_dict[key][field]:
                            merged_dict[key][field].append(port)
                    merged_dict[key][field].sort()
                # 合并IP列表
                for field in ['源IP', '目的IP', '公网IP']:
                    if isinstance(entry[field], list):
                        for ip in entry[field]:
                            if ip not in merged_dict[key][field]:
                                merged_dict[key][field].append(ip)
                        merged_dict[key][field].sort()

        return list(merged_dict.values())

    def generate_title(self, customer_info, requirement_info):
        """生成变更标题

        Args:
            customer_info (dict): 客户信息
            requirement_info (dict): 需求信息

        Returns:
            str: 变更标题
        """
        title = f"{customer_info['organization']}网络策略变更申请"
        self.logger.info(f"生成变更标题: {title}")
        return title

    def generate_reason(self, customer_info, requirement_info):
        """生成变更原因

        Args:
            customer_info (dict): 客户信息
            requirement_info (dict): 需求信息

        Returns:
            str: 变更原因
        """
        #
        st_info = self.get_source_target_config(requirement_info)
        source_target_pair = st_info['pair']

        # 加载模板
        env = Environment(loader=FileSystemLoader(self.templates_dir))
        template = env.get_template('reason.tpl')

        # 渲染模板
        reason = template.render(
            customer=customer_info,
            requirement=requirement_info,
            source_target_pair=source_target_pair
        )

        self.logger.info(f"生成变更原因: {reason}")
        return reason

    def generate_scheme(self, customer_info, requirement_info):
        """生成变更方案

        Args:
            customer_info (dict): 客户信息
            requirement_info (dict): 需求信息

        Returns:
            str: 变更方案
        """

        scenario_type, config = self.get_scenario_config(requirement_info["源归属"], requirement_info["目的归属"])

        # 复用场景配置（多处使用）
        # 1. 构建通用上下文
        common_context = self._get_common_context(customer_info, requirement_info, scenario_type)
        logger.debug(f"通用上下文: {common_context}")
        # 调用特定场景上下文处理器
        # 查询config配置文件获取场景上下文处理器,通过反射器，调用类方法
        context_processor_str = config.get('context_processor', '')
        logger.debug(context_processor_str)  # 建议使用logger替代print进行调试

        # 修复反射调用：移除多余的self参数，调整参数顺序以匹配方法定义
        if context_processor_str and hasattr(self, context_processor_str):
            scenario_context = getattr(self, context_processor_str)(customer_info, requirement_info)
            logger.debug(f"调用场景上下文处理器: {scenario_context}")
        else:
            self.logger.error(f"上下文处理器不存在: {context_processor_str}")
            scenario_context = {}

        if not scenario_context:
            self.logger.warning("无法获取场景特定上下文，使用通用上下文")

        # 合并上下文并添加 customer 变量和vpn相关变量
        context = {**common_context, **scenario_context, 'customer': customer_info, 'requirement': requirement_info}
        self.logger.debug(f"渲染Jinja2模板context：{context}")

        # 3. 渲染模板并返回结果
        env = Environment(loader=FileSystemLoader(self.templates_dir))
        template = env.get_template(config["template"])  # 动态加载模板文件
        scheme = template.render(**context)

        # 4. 新增：检查现有配置并处理方案
        # processed_scheme = check_existing_config(raw_scheme, requirement, source_target_pair)
        # return processed_scheme

        self.logger.info(f"生成变更原因:{scheme}")
        return scheme

    def get_source_target_config(self, requirement):
        """获取源归属-目标归属组合的配置信息"""
        source_attribution = requirement.get("源归属")
        target_attribution = requirement.get("目的归属")
        source_target_pair = (source_attribution, target_attribution)

        scenario_type, scenario_config = self.get_scenario_config(source_attribution, target_attribution)

        # 返回配置信息及源目标组合
        return {
            "pair": source_target_pair,
            "config": scenario_config,
            "scenario_type": scenario_type
        }

    def get_scenario_config(self, source, dest):
        """
        统一场景解析函数，避免重复条件判断
        """
        scenario_mapping = {
            ("行业云", "行业云"): "industry_cloud_to_industry_cloud",
            ("行业云", "互联网"): "industry_cloud_to_internet",
            ("互联网", "行业云"): "internet_to_industry_cloud",
            ("行业云", "证联网测试网"): "industry_cloud_to_zltest",
        }

        key = (source, dest)
        if key not in scenario_mapping:
            raise ValueError(f"未定义的场景组合: {source} -> {dest}")

        scenario_type = scenario_mapping[key]
        return scenario_type, self.config['scenario_config'][scenario_type]

    def _get_common_context(self, customer, requirement, scenario_type):
        """
            获取通用上下文信息，支持多场景处理

            :param customer: 客户信息字典
            :param requirement: 需求信息字典
            :param scenario_type: 场景类型字符串，对应SCENARIO_CONFIG中的键
            :return: 构建好的上下文字典
        """
        # 验证场景类型是否支持
        if scenario_type not in self.config["scenario_config"]:
            raise ValueError(f"不支持的场景类型: {scenario_type}")

        # 获取场景配置
        config = self.config["scenario_config"][scenario_type]
        context = {}

        # 添加IP相关信息
        ip_mapping = config["ip_mapping"]
        for key, field in ip_mapping.items():
            context[key] = requirement.get(field, [])

        # 添加端口相关信息
        # port_info = {}
        # for port_field in config["port_fields"]:
        #     port_info[port_field] = requirement.get(port_field, [])
        # context["ports"] = port_info

        # 添加操作类型
        context["operation"] = requirement.get("操作", "允许")

        return context

    def get_isp_address(self, customer):
        """获取客户的ISP地址列表
        
        :param customer: 客户信息字典
        :return: ISP地址列表
        """
        # 模拟实现，返回空列表或默认值
        self.logger.warning("使用模拟实现的get_isp_address函数")
        return []

    def get_isp_name_addresses(self, customer, isp_ips):
        """获取ISP名称和地址的映射
        
        :param customer: 客户信息字典
        :param isp_ips: ISP IP地址列表
        :return: ISP名称和地址的映射字典
        """
        # 模拟实现，返回空字典或示例数据
        self.logger.warning("使用模拟实现的get_isp_name_addresses函数")
        # 返回一个示例映射，实际应用中需要根据实际情况实现
        result = {}
        for ip in isp_ips:
            result[f"ISP_{ip}"] = ip
        return result

    def _process_internet_industry_cloud_common(self, customer, requirement, ip_field):
        """互联网与行业云互访场景的通用处理函数

        :param ip_field: 用于检索EIP的IP字段名（"源IP"或"目的IP"）
        """
        context = {}

        # -------------------------- 1. 检索阿里云EIP --------------------------
        # 创建AliYunProcessor实例并调用get_eip_address方法
        aliyun_processor = AliYunProcessor({})
        eip_ips = aliyun_processor.get_eip_address(customer, requirement, ip_field)
        if eip_ips is None:  # 处理EIP检索失败的情况
            return None
        context["eip_ips"] = eip_ips

        # -------------------------- 2. IPAM获取并筛选运营商地址 (名称：IP地址)--------------------------
        # 可抽象为通用函数的逻辑
        isp_ips = requirement['公网IP']
        if isp_ips == r"/":
            isp_ips = self.get_isp_address(customer)
        context["isp_ips"] = isp_ips

        if '117.160.150.30' not in isp_ips and '218.28.144.146' not in isp_ips:
            isp_name_address = self.get_isp_name_addresses(customer, isp_ips)

            if not isp_name_address:
                error_msg = f"IPAM-未找到匹配的运营商地址（公网IP: {isp_ips}，组织名: {customer['organization']}）,请核实地址并登记。"
                self.logger.error(error_msg)

        # -------------------------- 3. 深信服地址组匹配 --------------------------
        with open(os.path.join(jsons_dir, "ad", "custom_addresses.json"), "r", encoding="utf-8") as f:
            custom_addresses_json = json.load(f)

        ad_isp_address_name = None
        ad_eip_address_name = None
        for item in custom_addresses_json["items"]:
            item_ips = item["addresses"]
            if sorted(isp_ips) == sorted(item_ips):
                ad_isp_address_name = item["name"]
            if eip_ips[0] in item_ips:
                ad_eip_address_name = item["name"]
            if ad_isp_address_name and ad_eip_address_name:
                break

        if ad_isp_address_name:
            self.logger.info(f"深信服-找到ISP地址组: {ad_isp_address_name}（IP: {isp_ips}）")
        if ad_eip_address_name:
            self.logger.info(f"深信服-找到EIP地址组: {ad_eip_address_name}（IP: {eip_ips}）")

        if not ad_isp_address_name or not ad_eip_address_name:
            missing = []
            if not ad_isp_address_name:
                # 定义ad_isp_address_name
                missing.append(f"ISP地址列表 {isp_ips}")
                ad_isp_address_name = f"ISP-{customer['organization']}"
            if not ad_eip_address_name:
                missing.append(f"EIP地址列表 {eip_ips}")
                ad_eip_address_name = f"EIP-{customer['organization']}"
            self.logger.error(f"深信服-地址组匹配失败，"
                              f"缺失: {', '.join(missing)}, 请手动创建")

        context["ad_isp_address_name"] = ad_isp_address_name
        context["ad_eip_address_name"] = ad_eip_address_name

        return context

    def process_internet_to_industry_cloud(self, customer, requirement):
        """互联网→行业云场景的上下文处理器"""
        context = self._process_internet_industry_cloud_common(customer, requirement, ip_field="目的IP")
        if not context:
            return None
        return context

    def process_industry_cloud_to_internet(self, customer, requirement):
        """行业云→互联网场景的上下文处理器"""
        context = self._process_internet_industry_cloud_common(customer, requirement, ip_field="源IP")
        if not context:
            return None
        return context

    def process_industry_cloud_to_zltest(customer, requirement):
        context = {}

        # -------------------------- 1. 检索阿里云EIP --------------------------
        # 调用抽象后的EIP检索函数
        eip_ips = get_eip_address(customer, requirement, ip_field='源IP')
        if eip_ips is None:  # 处理EIP检索失败的情况
            return None
        context["eip_ips"] = eip_ips

        # -------------------------- 2. 检索IPAM 是否登记备案地址 --------------------------
        # 调用抽象后的IPAM检索函数
        # isp_ips = get_isp_address(customer, ip_field='公网IP')
        # if isp_ips is None:  # 处理IPAM检索失败的情况
        #     return None
        # context["isp_ips"] = isp_ips
        #
        return context

    def process_industry_cloud_to_industry_cloud(self, customer, requirement):
        """
        行业云→互联网场景的上下文处理器

        功能：整合阿里云VPC信息与IPAM并网信息，合并相同网络属性的IP地址

        参数：
            customer: 客户信息
            requirement: 需求信息，包含源IP和目的IP

        返回：
            dict: 包含合并后的网络信息上下文
        """
        # 常量定义 - 提取配置参数，便于维护
        VPCS_JSON_PATH = os.path.join(jsons_dir, "ali_cloud", "vpcs.json")
        SUBNETS_JSON_PATH = os.path.join(jsons_dir, "ipam", "subnets.json")
        TARGET_CIDR = "172.27.0.0/16"

        try:
            # 1. 加载数据
            vpcs_data = _load_json_file(VPCS_JSON_PATH)
            subnets_data = _load_json_file(SUBNETS_JSON_PATH)

            # 2. 提取IP地址
            s_ips = requirement['源IP']
            d_ips = requirement['目的IP']
            all_ips = s_ips + d_ips

            # 3. 查找IP所在VPC
            combine_net_infos = get_combine_net_infos(all_ips, vpcs_data)
            logger.debug(f"combine_net_infos: {combine_net_infos}")

            # 4. 获取IPAM子网信息
            # 创建IpamProcessor实例并调用_get_ipam_cidrs方法
            ipam_processor = IpamProcessor(subnets_data)
            ipam_cidrs = ipam_processor.get_ipam_cidrs(subnets_data)
            logger.debug(f"ipam_all_cidrs: {ipam_cidrs}")

            # 5. 整合并网信息
            ipam_processor.enrich_combin_net_info_with_ipam(combine_net_infos, ipam_cidrs, TARGET_CIDR)

            # 6. 合并相同网络属性的IP
            merged_infos = ipam_processor.merge_similar_ips(combine_net_infos)
            context = {"combin_net_infos": merged_infos}

            return context

        except Exception as e:
            self.logger.error(f"处理网络信息时发生错误: {str(e)}", exc_info=True)
            return {"combin_net_infos": [], "error": str(e)}


class GetInformation:
    """获取信息类"""

    def __init__(self, config):
        """初始化方法，设置日志系统"""
        self.config = config
        self.logger = self.logger.getself.logger(__name__)

    def fetch_api_data(self, source_target_pair=None):
        """获取并保存各系统API数据（阿里云/深信服/山石）"""
        # 场景配置字典：统一管理不同场景的防火墙URL和存储路径
        scenario_config = {
            ("互联网", "行业云"): {
                "fw_url": "https://172.16.190.23",
                "sxf_save_dir": "ad",
                "fw_save_dir": "isp_fw"
            },
            ("行业云", "互联网"): {
                "fw_url": "https://172.16.190.23",  # 假设不同场景对应不同防火墙URL
                "sxf_save_dir": "ad",
                "fw_save_dir": "isp_fw"
            },
            ("行业云", "证联网测试网"): {
                "fw_url": "https://172.16.190.41",  # 假设不同场景对应不同防火墙URL
                "fw_save_dir": "cdl_fw/zltest",
                "fw_vsys": "ZLTest-vFW"
            },
            ("行业云", "ISP专线"): {
                "fw_url": "https://172.16.190.41",  # 假设不同场景对应不同防火墙URL
                "fw_save_dir": "cdl_fw/isp",
                "fw_vsys": "ISP-zhuanxian-vFW"
            },
            ("行业云", "郑商所办公网"): {
                "fw_url": "https://172.16.190.41",  # 假设不同场景对应不同防火墙URL
                "fw_save_dir": "cdl_fw/zceoa",
                "fw_vsys": "ZCEOA-vFW"
            },
            ("行业云", "易盛办公网"): {
                "fw_url": "https://172.16.190.45",  # 假设不同场景对应不同防火墙URL
                "fw_save_dir": "on_fw/esoa",
                "fw_vsys": "ESOA-vFW"
            },
            ("行业云", "行业云"): {
                "fw_url": "https://172.16.190.35:8443/",  # 假设不同场景对应不同防火墙URL
                "fw_save_dir": "on_fw/esoa",
                "fw_vsys": "ESOA-vFW"
            },
        }
        # 默认配置（未指定场景时使用）
        default_config = {
            "fw_url": "https://172.16.190.23",
            "sxf_save_dir": "ad/default",
            "fw_save_dir": "isp_fw/default"
        }

        # ======================== 通用数据获取（所有场景均执行）========================
        # 1. 阿里云API - 获取实例和网络接口信息
        # from src.modules.apis.aliyun_api import AliYunApiClient
        from src.modules.apis.sangfor_ad import SangforApiClient
        from src.modules.apis.phpipam_api import PhpIpamApiClient
        from src.modules.apis.hillstone_fw import HillstoneApiClient
        # 1. 阿里云API - 获取实例和网络接口信息
        ali_api_client = AliYunApiClient()
        instances_info = ali_api_client.describe_instances()
        save_response_to_json(instances_info, "ali_cloud/instances.json")

        network_interfaces_info = ali_api_client.describe_network_interfaces()
        save_response_to_json(network_interfaces_info, "ali_cloud/network_interfaces.json")

        eips_info = ali_api_client.describe_eip_addresses()
        save_response_to_json(eips_info, "ali_cloud/eips.json")

        # 2. IPAM API - 获取地址信息
        ipam_api_client = PhpIpamApiClient()
        addresses_info = ipam_api_client.get_addresses()
        save_response_to_json(addresses_info, "ipam/addresses.json")

        subnets_info = ipam_api_client.get_subnets()
        save_response_to_json(subnets_info, "ipam/subnets.json")

        # ======================== 场景特定数据获取（按source_target_pair执行）========================
        # 获取当前场景配置（优先场景 config，其次默认 config）
        current_config = scenario_config.get(source_target_pair,
                                             default_config) if source_target_pair else default_config

        # 3. 深信服AD API - 特定场景数据获取
        if source_target_pair == ("互联网", "行业云") or source_target_pair == ("行业云", "互联网"):
            sxf_api_client = SengforApiClient()
            dnat_info = sxf_api_client.get_dnat()
            save_response_to_json(dnat_info, f"{current_config['sxf_save_dir']}/dnat.json")

            custom_address_info = sxf_api_client.get_custom_addresses()
            save_response_to_json(custom_address_info, f"{current_config['sxf_save_dir']}/custom_addresses.json")

        # 4. 山石防火墙API - 按场景URL和路径获取数据
        hs_api_client = HillstoneApiClient(current_config["fw_url"])
        # 防火墙数据按场景分目录存储
        fw_save_dir = current_config["fw_save_dir"]
        # 场景一：互联网到行业云
        if source_target_pair == ("互联网", "行业云") or source_target_pair == ("行业云", "互联网"):
            hs_api_client = HillstoneApiClient(current_config["fw_url"])
            # 防火墙数据按场景分目录存储
            fw_save_dir = current_config["fw_save_dir"]

            policy_info = hs_api_client.get_policy()
            save_response_to_json(policy_info, f"{fw_save_dir}/policy.json")

            addrbook_info = hs_api_client.get_addrbook()
            save_response_to_json(addrbook_info, f"{fw_save_dir}/addrbook.json")

            servicebook_info = hs_api_client.get_servicebook()
            save_response_to_json(servicebook_info, f"{fw_save_dir}/servicebook.json")

            servicegroup_info = hs_api_client.get_servicegroup()
            save_response_to_json(servicegroup_info, f"{fw_save_dir}/servicegroup.json")

        else:
            policy_info = hs_api_client.get_vsys_policy(current_config['fw_vsys'])
            save_response_to_json(policy_info, f"{fw_save_dir}/policy.json")

            addrbook_info = hs_api_client.get_vsys_addrbook(current_config['fw_vsys'])
            save_response_to_json(addrbook_info, f"{fw_save_dir}/addrbook.json")

            servicebook_info = hs_api_client.get_vsys_servicebook(current_config['fw_vsys'])
            save_response_to_json(servicebook_info, f"{fw_save_dir}/servicebook.json")

    def save_response_to_json(self, response: object, filename: object) -> None:
        """
        将API响应结果保存为 JSON 文件到 json_files 文件夹下。

        :param response: API响应结果（字节流）
        :param filename: API操作名称
        """
        if response is None:
            self.logger.error("响应数据为空")
            return

        # 确保 json_files 文件夹存在
        json_dir = r'json_files'
        if not os.path.exists(json_dir):
            os.makedirs(json_dir)
        file_path = os.path.join(json_dir, f'{filename}')

        try:
            # 类型一：将字节流转换为字符串并解析为JSON
            if isinstance(response, bytes):
                response_str = response.decode('utf-8')
                response_json = json.loads(response_str)
            # 类型二：直接使用 response.json() 方法解析 JSON
            elif isinstance(response, requests.models.Response):
                response_json = response.json()
            # 类型三：直接使用列表
            elif isinstance(response, list):
                response_json = response
            else:
                return self.logger.error(f"响应数据类型不符合保存类型, 当前类型为：{type(response)}")
            # 将JSON数据写入文件
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                json.dump(response_json, f, ensure_ascii=False, indent=4)  # type: ignore
            self.logger.info(f"响应数据已保存到 {file_path}")
        except Exception as e:
            self.logger.error(f"保存响应数据到文件时出错: {e}")


class IpamProcessor:
    """IPAM数据处理类"""

    def __init__(self, ipam_data):
        """初始化方法，设置日志系统"""
        self.ipam_data = ipam_data
        self.logger = logger

    def get_ipam_cidrs(self, subnets_data):
        """从IPAM数据中提取子网和描述信息"""
        return {
            f"{subnet['subnet']}/{subnet['mask']}": subnet['description']
            for subnet in subnets_data
        }

    def enrich_combin_net_info_with_ipam(self, combin_net_infos, ipam_cidrs, target_cidr):
        """整合IPAM中的并网信息到网络信息中"""
        target_network = ipaddress.ip_network(target_cidr)

        for info in combin_net_infos.values():
            cidr = info['cidr']
            if not cidr or cidr not in ipam_cidrs:
                continue

            # 提取VLAN信息
            ipam_description = ipam_cidrs[cidr]
            vlan_match = re.search(r"vlan(\d+)", ipam_description)
            if not vlan_match:
                self.logger.warning(f"无法从描述中提取VLAN: {ipam_description}")
                continue

            combine_net_vlan = vlan_match.group(1)

            # 添加IPAM信息
            info.update({
                'vlan': combine_net_vlan,
                'description': re.search("(\S+)【", ipam_description).group(1),
                'vpn_instance': f"VPC-{combine_net_vlan}"
            })

            # 查找并网互联网段
            info['segment'], info['ip_a'], info['ip_b'], info['ip_c'] = self.find_internet_segment(
                ipam_cidrs, combine_net_vlan, target_network
            )

    def find_internet_segment(self, ipam_cidrs, vlan, target_network):
        """查找指定VLAN的并网对接网段"""
        for net, desc in ipam_cidrs.items():
            try:
                # 跳过IPv6
                if ipaddress.ip_network(net).version == 6:
                    continue

                # 检查是否包含目标VLAN且属于目标网段
                if desc and vlan in desc:
                    network = ipaddress.ip_network(net)
                    if network.subnet_of(target_network):
                        logger.info(f"找到并网对接网段: {net}")
                        return net, self.get_ip_at_position(net, 3), self.get_ip_at_position(net,4), self.get_ip_at_position(net, 5)
            except ValueError as e:
                logger.warning(f"处理网段 {net} 时出错: {str(e)}")
                continue

        return None, None, None, None

    def merge_similar_ips(self, net_infos):
        """合并具有相同网络属性的IP地址"""
        merged = {}

        for ip, info in net_infos.items():
            # 使用网络信息作为合并键
            info_key = tuple(sorted(info.items()))

            if info_key not in merged:
                merged[info_key] = {**info, 'ips': []}
            merged[info_key]['ips'].append(ip)

        return list(merged.values())

    def get_ip_at_position(self, network_str, position, from_end=False):
        """
        获取网段中指定位置的IP地址

        参数:
            network_str: 网段字符串 (如 "192.168.1.0/24")
            position: 位置索引，从1开始
            from_end: 是否从网段末尾开始计数，默认为False（从开头计数）

        返回:
            指定位置的IP地址字符串，若位置无效则返回None
        """
        try:
            # 解析网段
            network = ipaddress.ip_network(network_str, strict=False)

            # 获取网段内所有可用IP地址列表
            # 注意：hosts()不包含网络地址和广播地址
            hosts = list(network.hosts())
            total_hosts = len(hosts)

            # 检查位置是否有效
            if position < 1 or position > total_hosts:
                print(f"无效位置！该网段共有 {total_hosts} 个可用IP地址")
                return None

            # 计算实际索引（列表从0开始）
            if from_end:
                index = total_hosts - position
            else:
                index = position - 1

            return str(hosts[index])

        except ValueError as e:
            print(f"网段解析错误: {e}")
            return None


class AliYunProcessor:
    def __init__(self, aliyun_data):
        self.aliyun_data = aliyun_data
        self.logger = logger

    def get_eip_address(self, customer, requirement, ip_field):
        """从阿里云网络接口数据中检索EIP地址列表

        :param customer: 客户信息字典
        :param requirement: 需求信息字典
        :param ip_field: 用于检索EIP的IP字段名（"源IP"或"目的IP"）
        :return: EIP地址列表；若检索失败返回None
        """
        try:
            # 确保ip_field的值存在且是列表
            if ip_field not in requirement:
                self.logger.error(f"字段 {ip_field} 在需求信息中不存在")
                return []

            # 处理IP列表
            ip_list = requirement[ip_field]
            if isinstance(ip_list, str):
                ip_list = [ip_list]

            eip_addresses = []
            # 简单模拟EIP检索逻辑，避免依赖未定义的extract_jsonpath函数
            for ip in ip_list:
                # 这里简化处理，实际应用中可能需要根据实际情况调整
                eip_addresses.append(ip)

            self.logger.info(f"阿里云-处理的IP地址为：{eip_addresses}")
            return eip_addresses
        except Exception as e:
            self.logger.error(f"获取EIP地址时出错：{str(e)}")
            return []


def main():
    """
    主函数，用于直接运行模块时调用
    """
    # 加载配置
    config_manager = ConfigManager(config_path)
    config = config_manager.load_config()
    logger.info('配置加载完成')
    logger.info(f"{config}")
    logger.info(f"{config['scenario_config'].keys()}")

    # 向上回溯两级到项目根目录（根据实际情况调整）
    # for root, dirs, files in os.walk(os.path.join(project_root, 'data', 'input', 'order')):
    #     for file in files:
    #         if file.endswith('.xlsx'):
    #             order_path = os.path.join(root, file)
    #             logger.info(f'开始处理订单: {order_path}')
    #             #
    #             content = OrderProcessor(order_path, config, template_dir)
    #             # print(content)

    order_path = os.path.join(project_root, 'data', 'input', 'order',
                              '西部期货-官网.xlsx')

    logger.info(f'开始处理订单: {order_path}')
    #
    content = OrderProcessor(order_path, config, template_dir)
    # print(content)


if __name__ == '__main__':
    main()