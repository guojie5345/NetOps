#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
基线检查模块

该模块提供网络设备基线配置检查功能，支持多种设备平台，可检查配置合规性、接口状态和系统服务状态。
"""

import yaml
import datetime
from jinja2 import Template
import os
import re
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any
import logging
from openpyxl import Workbook

# 导入SSH采集器
from src.modules.collection.ssh_collector import SSHCollector
from src.utils.logger import get_module_logger

# 设置日志
logger = get_module_logger(__name__)


class ConfigRule:
    """配置规则类"""
    def __init__(self, rule: str, description: str, regex: bool = False):
        self.rule = rule
        self.description = description
        self.regex = regex
        if regex:
            try:
                self.pattern = re.compile(rule)
            except re.error as e:
                logger.error(f"无效的正则表达式模式 '{rule}': {e}")
                self.pattern = None
        else:
            self.pattern = None

    def check_compliance(self, config: str) -> bool:
        """检查配置是否符合规则
        
        Args:
            config: 设备配置字符串
            
        Returns:
            bool: 是否符合规则
        """
        if self.regex and self.pattern:
            return bool(self.pattern.search(config))
        return self.rule in config


class StatusCheck:
    """状态检查基类"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.platform_commands = {}
        self.success_patterns = {}  # 结构：{平台：[re.Pattern]}

    def add_platform_command(self, platform: str, command: str):
        """添加平台特定的命令
        
        Args:
            platform: 设备平台名称
            command: 要执行的命令
        """
        self.platform_commands[platform] = command

    def set_success_pattern(self, platform: str, pattern: str, flags=re.IGNORECASE):
        """设置成功匹配的模式
        
        Args:
            platform: 设备平台名称
            pattern: 正则表达式匹配模式
            flags: 正则表达式标志
            
        Raises:
            ValueError: 正则表达式无效时抛出
        """
        if platform not in self.success_patterns:
            self.success_patterns[platform] = []
        try:
            compiled = re.compile(pattern, flags)
            self.success_patterns[platform].append(compiled)
        except re.error as e:
            raise ValueError(f"无效的正则表达式 '{pattern}': {e}")

    def check_output(self, output: str, platform: str) -> bool:
        """检查命令输出是否符合预期
        
        Args:
            output: 命令输出结果
            platform: 设备平台名称
            
        Returns:
            bool: 是否符合预期
        """
        patterns = self.success_patterns.get(platform, [])
        return any(pattern.search(output) for pattern in patterns)

    def get_command(self, platform: str) -> str:
        """获取平台对应的命令
        
        Args:
            platform: 设备平台名称
            
        Returns:
            str: 命令字符串或None
        """
        return self.platform_commands.get(platform)


class NTPStatusCheck(StatusCheck):
    """NTP状态检查类"""

    def __init__(self):
        super().__init__("ntp_status", "NTP同步状态检查")
        # 配置各平台的命令
        self.add_platform_command("cisco_ios", "show ntp status")
        self.add_platform_command("hp_comware", "display ntp-service status")
        self.add_platform_command("huawei_vrp", "display ntp status")
        self.add_platform_command("cisco_nxos", "show ntp peer-status")
        # 配置成功匹配模式
        self.set_success_pattern("cisco_ios", r"\ssynchronized")
        self.set_success_pattern("hp_comware", r"\ssynchronized")
        self.set_success_pattern("huawei_vrp", r"\ssynchronized")
        self.set_success_pattern("cisco_nxos", r"\*\d+")


class BaselineChecker:
    """基线检查主类"""
    
    def __init__(self, rules_file=None, max_workers: int = 10):
        """初始化基线检查器
        
        Args:
            rules_file: 规则文件路径
            max_workers: 最大工作线程数
        """
        # 如果未提供规则文件路径，使用默认路径
        if rules_file is None:
            # 获取当前文件所在目录的绝对路径
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # 向上找到项目根目录 (假设当前在 src/modules/baseline/ 目录下)
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
            rules_file = os.path.join(project_root, 'config', 'baseline_rules.yaml')
            
        self.rules = self._load_rules(rules_file)
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        # 初始化状态检查列表
        self.status_checks = [NTPStatusCheck()]
        # 加载HTML报告模板
        self.report_template = self._load_report_template()

    def _load_report_template(self) -> str:
        """加载HTML报告模板
        
        Returns:
            str: 报告模板内容
            
        Raises:
            FileNotFoundError: 模板文件不存在时抛出
        """
        # 获取当前文件所在目录的绝对路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 向上找到项目根目录 (假设当前在 src/modules/baseline/ 目录下)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        template_path = os.path.join(project_root, 'templates', 'baseline_report.html')
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            # 如果模板文件不存在，生成一个简单的模板
            logger.warning(f"模板文件不存在: {template_path}，将使用默认模板")
            return self._get_default_template()
        except Exception as e:
            logger.error(f"加载模板文件时出错: {e}")
            # 返回默认模板
            return self._get_default_template()
    
    def _get_default_template(self) -> str:
        """获取默认的HTML报告模板
        
        Returns:
            str: 默认模板内容
        """
        return '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>基线检查报告</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1, h2 { color: #333; }
        table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #4CAF50; color: white; }
        .pass { background-color: #d4edda; }
        .fail { background-color: #f8d7da; }
        .device-section { margin-bottom: 30px; }
    </style>
</head>
<body>
    <h1>基线检查报告</h1>
    <p>生成时间: {{ timestamp }}</p>
    
    {% for device in devices %}
    <div class="device-section">
        <h2>设备: {{ device.name }} ({{ device.hostname }})</h2>
        <table>
            <tr>
                <th>规则描述</th>
                <th>检查结果</th>
                <th>实际配置</th>
            </tr>
            {% for result in device.results %}
            <tr class="{{ 'pass' if result.compliant else 'fail' }}">
                <td>{{ result.description }}</td>
                <td>{{ '通过' if result.compliant else '未通过' }}</td>
                <td><pre>{{ result.actual_config }}</pre></td>
            </tr>
            {% endfor %}
        </table>
    </div>
    {% endfor %}
</body>
</html>'''

    def _load_rules(self, rules_file: str) -> Dict[str, List[ConfigRule]]:
        """加载基线规则
        
        Args:
            rules_file: 规则文件路径
            
        Returns:
            Dict[str, List[ConfigRule]]: 平台到规则列表的映射
        """
        try:
            with open(rules_file, 'r', encoding='utf-8') as f:
                raw_rules = yaml.safe_load(f)
                processed_rules = {}
                for platform, rules in raw_rules.items():
                    processed_rules[platform] = [
                        ConfigRule(
                            rule=rule['rule'],
                            description=rule['description'],
                            regex=rule.get('regex', False)
                        )
                        for rule in rules
                    ]
                return processed_rules
        except Exception as e:
            logger.error(f"加载规则文件时出错: {e}")
            return {}

    def check_compliance(self, config: str, rules: List[ConfigRule]) -> list:
        """检查配置是否符合规则列表
        
        Args:
            config: 设备配置字符串
            rules: 规则列表
            
        Returns:
            list: 检查结果列表
        """
        results = []
        for rule in rules:
            compliant = rule.check_compliance(config)
            results.append({
                'rule': rule.rule,
                'description': rule.description,
                'compliant': compliant,
                'actual_config': self._find_related_config(config, rule)
            })
        return results

    def _find_related_config(self, config: str, rule: ConfigRule) -> str:
        """查找配置中与规则相关的部分
        
        Args:
            config: 设备配置字符串
            rule: 配置规则
            
        Returns:
            str: 相关配置部分
        """
        if rule.regex and rule.pattern:
            matches = rule.pattern.finditer(config)
            matched_lines = [match.group(0) for match in matches]
        else:
            lines = config.split('\n')
            matched_lines = [line for line in lines if rule.rule in line]
        return '\n'.join(matched_lines) if matched_lines else "未找到相关配置"

    def _process_interface_status(self, interface_output: str, platform: str) -> List[str]:
        """处理接口状态输出
        
        Args:
            interface_output: 接口状态命令输出
            platform: 设备平台名称
            
        Returns:
            List[str]: 关闭的接口列表
        """
        down_interfaces = []
        for line in interface_output.split('\n'):
            if platform == 'cisco_ios':
                if 'notconnect' in line.lower():
                    interface_name = line.split()[0]
                    down_interfaces.append(interface_name)
            elif platform == 'hp_comware':
                if 'DOWN' in line:
                    parts = line.split()
                    down_interfaces.append(parts[0])
            elif platform == 'huawei_vrp':
                if 'down' in line.lower():
                    if ':' in line:
                        continue
                    parts = line.split()
                    if len(parts) >= 1:
                        down_interfaces.append(parts[0])
            elif platform == "cisco_nxos":
                if 'notconnec' in line.lower():
                    interface_name = line.split()[0]
                    down_interfaces.append(interface_name)
        return down_interfaces

    def check_device(self, device_info: Dict[str, Any]) -> Dict[str, Any]:
        """检查单个设备
        
        Args:
            device_info: 设备连接信息
            
        Returns:
            Dict[str, Any]: 检查结果
        """
        try:
            host = device_info.get('host', 'Unknown')
            logger.info(f"正在检查设备: {host}")

            # 定义平台命令映射
            platform_commands = {
                'cisco_ios': {
                    'config': 'show running-config',
                    'interface': 'show interfaces status'
                },
                'hp_comware': {
                    'config': 'display current-configuration',
                    'interface': 'display interface brief'
                },
                'huawei_vrp': {
                    'config': 'display current-configuration',
                    'interface': 'display interface brief'
                },
                'cisco_nxos': {
                    'config': 'show running-config',
                    'interface': 'show interface status'
                },
                'juniper_junos': {
                    'config': 'show configuration',
                    'interface': 'show interfaces brief'
                },
                'juniper_screenos': {
                    'config': 'get configuration',
                    'interface': 'get interface'
                }
            }

            # 创建SSH收集器并连接
            collector = SSHCollector(device_info)
            if not collector.connect():
                raise Exception(f"无法连接到设备 {host}")

            try:
                platform = device_info.get('device_type', '')
                if platform not in platform_commands:
                    raise ValueError(f"不支持的平台类型: {platform}")

                commands = platform_commands[platform]

                # 获取配置和接口状态
                config = collector.execute_command(commands['config'])
                interface_output = collector.execute_command(commands['interface'])

                # 处理接口状态
                admin_down_interfaces = self._process_interface_status(
                    interface_output, platform
                )

                # 修改获取适用规则的逻辑，确保规则不重复
                applicable_rules = []
                seen_rules = set()  # 用于追踪已添加的规则

                # 首先添加平台特定的规则
                if platform in self.rules:
                    for rule in self.rules[platform]:
                        rule_key = (rule.rule, rule.description)
                        if rule_key not in seen_rules:
                            applicable_rules.append(rule)
                            seen_rules.add(rule_key)

                # 然后添加通用规则（如果还没有添加过）
                for rule in self.rules.get('common', []):
                    rule_key = (rule.rule, rule.description)
                    if rule_key not in seen_rules:
                        applicable_rules.append(rule)
                        seen_rules.add(rule_key)

                # 执行配置检查
                check_results = self.check_compliance(config, applicable_rules)

                # 添加接口状态检查结果
                interface_check = {
                    'rule': 'interface shutdown',
                    'description': '主动关闭接口检查',
                    'compliant': len(admin_down_interfaces) == 0,
                    'actual_config': ', '.join(admin_down_interfaces) if admin_down_interfaces else '所有接口状态正常'
                }
                check_results.append(interface_check)

                # 执行状态检查
                status_results = []
                for check in self.status_checks:
                    command = check.get_command(platform)
                    if command:
                        try:
                            status_output = collector.execute_command(command)
                            compliant = check.check_output(status_output, platform)
                            status_results.append({
                                'rule': check.name,
                                'description': check.description,
                                'compliant': compliant,
                                'actual_config': status_output.strip() if status_output else "无输出"
                            })
                        except Exception as e:
                            logger.error(f"执行状态检查 {check.name} 失败: {str(e)}")
                            status_results.append({
                                'rule': check.name,
                                'description': check.description,
                                'compliant': False,
                                'actual_config': f"检查失败: {str(e)}"
                            })

                # 合并所有检查结果
                check_results.extend(status_results)

                return {
                    'device_name': host,
                    'device_hostname': host,
                    'check_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'results': check_results,
                    'failed': False
                }
            finally:
                # 断开连接
                collector.disconnect()

        except Exception as e:
            logger.error(f"设备 {device_info.get('host', 'Unknown')} 检查失败: {str(e)}", exc_info=True)
            return {
                'device_name': device_info.get('host', 'Unknown'),
                'device_hostname': device_info.get('host', 'Unknown'),
                'check_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'results': [],
                'failed': True,
                'error': str(e)
            }

    def check_baseline(self, devices: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """执行基线检查
        
        Args:
            devices: 设备列表
            
        Returns:
            Dict[str, Dict[str, Any]]: 设备到检查结果的映射
        """
        try:
            logger.info(f"开始基线检查，共 {len(devices)} 台设备")
            
            # 执行设备检查
            results = {}
            futures = {}
            
            # 提交所有设备检查任务
            for device in devices:
                host = device.get('host', 'Unknown')
                futures[host] = self.executor.submit(self.check_device, device)
            
            # 获取所有任务结果
            for host, future in futures.items():
                try:
                    results[host] = future.result()
                except Exception as e:
                    logger.error(f"获取设备 {host} 检查结果时发生错误: {str(e)}")
                    results[host] = {
                        'device_name': host,
                        'device_hostname': host,
                        'check_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'results': [],
                        'failed': True,
                        'error': str(e)
                    }

            # 生成报告
            self._generate_report(results)
            self._generate_excel_report(results)

            # 统计检查结果
            success_count = sum(1 for result in results.values() if not result.get('failed', False))
            failed_count = len(results) - success_count
            
            logger.info(f"基线检查完成: 成功 {success_count} 台, 失败 {failed_count} 台")
            
            return results

        except Exception as e:
            logger.error(f"执行基线检查时发生错误: {str(e)}", exc_info=True)
            raise
        finally:
            # 清理线程池
            self.executor.shutdown(wait=True)

    def _generate_report(self, results: Dict[str, Dict[str, Any]]):
        """生成HTML报告
        
        Args:
            results: 检查结果字典
        """
        # 准备报告数据
        report_data = {
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'devices': []
        }

        for host, result in results.items():
            if result.get('failed', False):
                continue
            report_data['devices'].append({
                'name': result['device_name'],
                'hostname': result['device_hostname'],
                'results': result['results']
            })

        # 生成报告
        template = Template(self.report_template)
        report_html = template.render(**report_data)

        # 保存报告
        os.makedirs('reports', exist_ok=True)
        report_file = f"reports/baseline_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_html)
        logger.info(f"HTML报告已生成: {report_file}")

    def _generate_excel_report(self, results: Dict[str, Dict[str, Any]]):
        """生成 Excel 报告
        
        Args:
            results: 检查结果字典
        """
        wb = Workbook()
        ws = wb.active
        ws.title = "基线检查报告"

        # 添加表头
        headers = ["设备名称", "管理IP", "规则描述", "检查结果", "实际配置"]
        ws.append(headers)

        for host, result in results.items():
            if result.get('failed', False):
                # 添加失败的设备信息
                device_name = result.get('device_name', host)
                device_hostname = result.get('device_hostname', host)
                ws.append([device_name, device_hostname, "设备连接或检查失败", "未通过", result.get('error', '未知错误')])
                continue
                
            device_name = result['device_name']
            device_hostname = result['device_hostname']
            for check_result in result['results']:
                rule_description = check_result['description']
                compliant = "通过" if check_result['compliant'] else "未通过"
                actual_config = check_result['actual_config']
                ws.append([device_name, device_hostname, rule_description, compliant, actual_config])

        # 保存 Excel 文件
        os.makedirs('reports', exist_ok=True)
        report_file = f"reports/baseline_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        wb.save(report_file)
        logger.info(f"Excel 报告已生成: {report_file}")


def check_devices_baseline(device_list: List[Dict[str, Any]], rules_file=None, max_workers: int = 10) -> Dict[str, Dict[str, Any]]:
    """
    检查设备列表的基线配置
    
    Args:
        device_list: 设备列表
        rules_file: 规则文件路径
        max_workers: 最大工作线程数
        
    Returns:
        Dict[str, Dict[str, Any]]: 设备到检查结果的映射
    """
    # 创建检查器实例
    checker = BaselineChecker(rules_file=rules_file, max_workers=max_workers)
    
    # 执行基线检查
    results = checker.check_baseline(device_list)
    
    return results


if __name__ == "__main__":
    # 示例用法
    import json
    
    # 示例设备配置
    devices = [
        {
            "device_type": "cisco_ios",
            "host": "192.168.80.21",
            "username": "nms",
            "password": "cisco",
            "port": 22
        }
    ]
    
    try:
        # 运行基线检查
        print("开始基线检查...")
        results = check_devices_baseline(devices)
        print(f"基线检查完成，共 {len(results)} 台设备")
        
        # 打印结果统计
        success_count = sum(1 for result in results.values() if not result.get('failed', False))
        print(f"成功: {success_count} 台, 失败: {len(results) - success_count} 台")
        
    except Exception as e:
        logger.error(f"程序执行失败: {str(e)}", exc_info=True)
        print(f"程序执行失败: {str(e)}")
