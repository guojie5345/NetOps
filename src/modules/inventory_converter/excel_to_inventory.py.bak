#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Excel到Inventory转换模块

该模块负责将Excel主机配置文件转换为Netmiko可用的inventory文件，支持多种格式输出（JSON、简化JSON、INI）。
"""

import pandas as pd
import os
import json
import sys
import yaml
from datetime import datetime

# 获取当前文件的绝对路径并添加项目根目录到系统路径
current_file = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file))))
# 将项目根目录添加到系统路径中，使Python能够正确解析以'src'开头的导入
sys.path.insert(0, project_root)

from src.utils.logger import setup_logger

# 在模块级别初始化一次日志系统
logger = setup_logger()

# 加载设备映射配置
device_mapping_config_path = os.path.join(project_root, 'config', 'device', 'device_mapping_config.json')
if os.path.exists(device_mapping_config_path):
    with open(device_mapping_config_path, 'r', encoding='utf-8') as f:
        DEVICE_MAPPING_CONFIG = json.load(f)
else:
    # 默认配置
    DEVICE_MAPPING_CONFIG = {
        "template_mapping": {
            "cisco_ios": ["cisco ios", "cisco_ios"],
            "cisco_nxos": ["cisco nxos", "n3548"],
            "huawei_vrp": ["huawei", "vrp"],
            "juniper_junos": ["juniper"],
            "juniper_screenos": ["screenos"],
            "hp_procurve": ["procurve"],
            "hp_comware": ["hp", "comware", "h3c"],
            "linux": ["linux"],
            "windows": ["windows"]
        },
        "hostname_mapping": {
            "cisco_ios": ["cisco", "3750", "3850", "2960", "4500", "4948"],
            "huawei_vrp": ["huawei", "eudemon", "s5700", "s6700", "s7700", "s9300"],
            "juniper_junos": ["junip"],
            "linux": ["linux"],
            "windows": ["windows"],
            "hp_procurve": ["hp", "procurve"],
            "hp_comware": ["h3c", "comware"]
        },
        "network_device_types": [
            "cisco_ios",
            "cisco_nxos",
            "huawei_vrp",
            "juniper_junos",
            "juniper_screenos",
            "hp_procurve",
            "hp_comware"
        ]
    }

class ExcelToInventoryConverter:
    """将Excel主机配置文件转换为Netmiko可用的inventory文件"""
    
    def __init__(self, excel_path, output_dir=None):
        """初始化转换器
        
        Args:
            excel_path (str): Excel文件路径
            output_dir (str, optional): 输出目录，默认使用当前目录
        """
        self.excel_path = excel_path
        self.output_dir = output_dir or os.path.dirname(excel_path)
        
        # 确保输出目录存在
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            logger.info(f"创建输出目录: {self.output_dir}")
        
        # 检查文件是否存在
        if not os.path.exists(self.excel_path):
            logger.error(f"Excel文件不存在: {self.excel_path}")
            raise FileNotFoundError(f"Excel文件不存在: {self.excel_path}")
    
    def read_excel_file(self):
        """读取Excel文件并返回数据"""
        try:
            # 使用pandas读取Excel文件
            df = pd.read_excel(self.excel_path)
            logger.info(f"成功读取Excel文件，共{len(df)}行数据")
            logger.info(f"列名: {list(df.columns)}")
            
            # 显示前几行数据，了解数据结构
            logger.debug(f"前5行数据预览:\n{df.head().to_string()}")
            
            return df
        except Exception as e:
            logger.error(f"读取Excel文件时出错: {str(e)}")
            raise
    
    def identify_host_columns(self, df):
        """识别包含主机配置信息的列
        
        Args:
            df (DataFrame): pandas DataFrame对象
            
        Returns:
            dict: 包含主机信息的列映射
        """
        # 常见的主机配置列名
        common_columns = {
            'ip': ['ip', 'ip地址', '主机ip', '主机ip地址', '地址', '服务器地址'],
            'hostname': ['hostname', '主机名', '显示名称', '设备名', '名称', 'device', 'device name'],
            'port': ['端口', 'ssh端口']
        }
        
        column_mapping = {}
        
        # 特殊处理：根据Excel文件内容，直接识别特定列
        if '接口1IP' in df.columns:
            column_mapping['ip'] = '接口1IP'
        
        if '主机名' in df.columns:
            column_mapping['hostname'] = '主机名'
        elif '显示名称' in df.columns:
            column_mapping['hostname'] = '显示名称'
        
        if '接口1端口' in df.columns:
            column_mapping['port'] = '接口1端口'
        
        # 如果特殊处理后还没有找到IP列，再使用通用方法
        if 'ip' not in column_mapping:
            # 遍历所有列，寻找匹配的列名
            for col in df.columns:
                col_lower = str(col).lower()
                
                for key, possible_names in common_columns.items():
                    for name in possible_names:
                        if name.lower() in col_lower:
                            column_mapping[key] = col
                            break
                    if key in column_mapping:
                        break
        
        # 如果仍然没有找到IP列，尝试检查哪些列可能包含IP地址
        if 'ip' not in column_mapping:
            for col in df.columns:
                # 尝试识别可能包含IP的列
                try:
                    if df[col].astype(str).str.match(r'\b(?:\d{1,3}\.){3}\d{1,3}\b').any():
                        column_mapping['ip'] = col
                        break
                except:
                    continue
        
        logger.info(f"识别到的主机配置列: {column_mapping}")
        return column_mapping
    
    def generate_inventory(self, df, column_mapping):
        """生成inventory字典
        
        Args:
            df (DataFrame): pandas DataFrame对象
            column_mapping (dict): 列映射
            
        Returns:
            dict: 生成的inventory字典
        """
        inventory = {
            'all': {
                'hosts': {},
                'children': {}
            }
        }
        
        # 按设备类型分组
        type_groups = {}
        
        # 遍历每行数据
        for index, row in df.iterrows():
            # 跳过空行
            if pd.isna(row[column_mapping.get('ip')]):
                continue
            
            # 检查状态列，如果存在且值为'禁用'，则跳过
            if '状态' in df.columns and not pd.isna(row['状态']) and row['状态'] == '禁用':
                continue
            
            host_data = {}
            hostname = None
            
            # 提取主机信息
            if 'hostname' in column_mapping and not pd.isna(row[column_mapping['hostname']]):
                hostname = str(row[column_mapping['hostname']])
            
            # 使用IP作为主机标识
            ip = str(row[column_mapping['ip']])
            
            # 验证IP地址格式
            if not self._is_valid_ip(ip):
                continue
            
            host_identifier = hostname or ip
            
            # 添加主机基本信息
            host_data['ansible_host'] = ip
            
            # 添加端口信息
            if 'port' in column_mapping and not pd.isna(row[column_mapping['port']]):
                try:
                    host_data['ansible_port'] = int(row[column_mapping['port']])
                except ValueError:
                    host_data['ansible_port'] = 22
            else:
                # 默认SSH端口
                host_data['ansible_port'] = 22
            
            # 尝试从关联模板推断设备类型（优先级最高）
            device_type = 'generic_termserver'  # 默认设备类型
            if '关联模板' in df.columns and not pd.isna(row['关联模板']):
                template_name = str(row['关联模板'])
                # 根据模板名称推断设备类型
                template_lower = template_name.lower()
                
                # 使用配置文件中的模板映射规则
                for dt, keywords in DEVICE_MAPPING_CONFIG.get('template_mapping', {}).items():
                    if any(keyword in template_lower for keyword in keywords):
                        device_type = dt
                        break
            
            # 如果没有从模板匹配到设备类型，则尝试从主机名推断
            if device_type == 'generic_termserver' and hostname:
                hostname_lower = hostname.lower()
                # 使用配置文件中的主机名映射规则
                for dt, keywords in DEVICE_MAPPING_CONFIG.get('hostname_mapping', {}).items():
                    if any(keyword in hostname_lower for keyword in keywords):
                        device_type = dt
                        break
            
            host_data['device_type'] = device_type
            
            # 如果有主机组信息，也添加到主机数据中
            if '主机组' in df.columns and not pd.isna(row['主机组']):
                host_data['host_groups'] = str(row['主机组'])
            
            # 添加到all.hosts
            inventory['all']['hosts'][host_identifier] = host_data
            
            # 添加到类型分组
            if device_type not in type_groups:
                type_groups[device_type] = []
            type_groups[device_type].append(host_identifier)
        
        # 创建类型分组
        for group_name, hosts in type_groups.items():
            inventory['all']['children'][group_name] = {
                'hosts': {host: {} for host in hosts}
            }
        
        logger.info(f"生成的inventory包含 {len(inventory['all']['hosts'])} 台主机")
        return inventory
    
    def _is_valid_ip(self, ip_str):
        """验证字符串是否为有效的IP地址
        
        Args:
            ip_str (str): 要验证的字符串
            
        Returns:
            bool: 是否为有效IP地址
        """
        try:
            parts = ip_str.split('.')
            if len(parts) != 4:
                return False
            for part in parts:
                num = int(part)
                if num < 0 or num > 255:
                    return False
            return True
        except:
            return False
            
    def save_inventory(self, inventory):
        """保存inventory文件
        
        Args:
            inventory (dict): 要保存的inventory字典
        """
        # 生成时间戳文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        inventory_file = os.path.join(self.output_dir, f"inventory_{timestamp}.json")
        
        # 保存为JSON格式
        with open(inventory_file, 'w', encoding='utf-8') as f:
            json.dump(inventory, f, ensure_ascii=False, indent=4)
        
        logger.info(f"Inventory文件已保存到: {inventory_file}")
        
        # 同时生成netmiko简单格式的inventory
        simple_inventory = {}
        for host, data in inventory['all']['hosts'].items():
            simple_inventory[host] = {
                'host': data['ansible_host'],
                'device_type': data['device_type'],
                'port': data['ansible_port']
            }
        
        simple_file = os.path.join(self.output_dir, f"inventory_simple_{timestamp}.json")
        with open(simple_file, 'w', encoding='utf-8') as f:
            json.dump(simple_inventory, f, ensure_ascii=False, indent=4)
        
        logger.info(f"简化版Inventory文件已保存到: {simple_file}")
        
        # 同时生成一个INI格式的inventory文件，方便某些场景使用
        ini_file = os.path.join(self.output_dir, f"inventory_{timestamp}.ini")
        with open(ini_file, 'w', encoding='utf-8') as f:
            f.write("[all]\n")
            for host, data in inventory['all']['hosts'].items():
                f.write(f"{host} ansible_host={data['ansible_host']} ansible_port={data['ansible_port']} device_type={data['device_type']}\n")
            f.write("\n")
            
            # 写入子组
            for group_name, group_data in inventory['all']['children'].items():
                f.write(f"[{group_name}]\n")
                for host in group_data['hosts']:
                    f.write(f"{host}\n")
                f.write("\n")
        
        logger.info(f"INI格式Inventory文件已保存到: {ini_file}")
        
        # 生成YAML格式的inventory文件
        self._save_yaml_inventory(inventory, timestamp)
        
        # 生成只包含网络设备的YAML文件
        self._save_network_devices_yaml_inventory(inventory, timestamp)
        
        return inventory_file, simple_file, ini_file
    
    def _save_yaml_inventory(self, inventory, timestamp):
        """保存YAML格式的inventory文件
        
        Args:
            inventory (dict): 要保存的inventory字典
            timestamp (str): 时间戳
        """
        # 生成hosts.yaml文件
        hosts_yaml_file = os.path.join(self.output_dir, "hosts.yaml")
        hosts_data = {}
        
        # 转换数据格式以匹配YAML格式
        for host, data in inventory['all']['hosts'].items():
            # 根据设备类型确定platform
            platform = data['device_type']
            
            # 映射设备类型到正确的platform
            platform_mapping = {
                'cisco_ios': 'cisco_ios',
                'cisco_nxos': 'cisco_nxos',
                'huawei': 'huawei_vrp',
                'huawei_vrp': 'huawei_vrp',
                'junos': 'juniper_junos',
                'juniper_junos': 'juniper_junos',
                'juniper_screenos': 'juniper_screenos',
                'hp_procurve': 'hp_procurve',
                'hp_comware': 'hp_comware',
                'linux': 'linux',
                'windows': 'windows'
            }
            
            # 如果有映射则使用映射值，否则使用原始值
            if platform in platform_mapping:
                platform = platform_mapping[platform]
            
            hosts_data[host] = {
                'groups': ['dev_group'],  # 默认分组
                'hostname': data['ansible_host'],
                'platform': platform
            }
        
        # 根据IP地址网段自动分配组
        self._auto_group_hosts_by_network(hosts_data)
        
        with open(hosts_yaml_file, 'w', encoding='utf-8') as f:
            yaml.dump(hosts_data, f, allow_unicode=True, default_flow_style=False, indent=2)
        
        logger.info(f"YAML格式hosts文件已保存到: {hosts_yaml_file}")
        
        # 生成groups.yaml文件
        groups_yaml_file = os.path.join(self.output_dir, "groups.yaml")
        groups_data = {
            'dev_group': {
                'username': 'esunny',
                'password': 'Bwxsgdj@2022'
            }
        }
        
        # 添加设备类型特定的组
        for group_name in inventory['all']['children'].keys():
            if group_name not in groups_data:
                groups_data[group_name] = {
                    'platform': group_name
                }
        
        # 添加网络分组
        self._add_network_groups(groups_data, hosts_data)
        
        with open(groups_yaml_file, 'w', encoding='utf-8') as f:
            f.write("---\n")
            yaml.dump(groups_data, f, allow_unicode=True, default_flow_style=False, indent=2)
        
        logger.info(f"YAML格式groups文件已保存到: {groups_yaml_file}")
        
        # 生成default.yaml文件
        default_yaml_file = os.path.join(self.output_dir, "default.yaml")
        default_data = {
            'username': '',
            'password': 'python',
            'platform': 'unknown',
            'connection_options': {
                'netmiko': {
                    'extras': {
                        'secret': 'esunnytrunk'
                    }
                }
            }
        }
        
        with open(default_yaml_file, 'w', encoding='utf-8') as f:
            f.write("---\n")
            yaml.dump(default_data, f, allow_unicode=True, default_flow_style=False, indent=2)
        
        logger.info(f"YAML格式default文件已保存到: {default_yaml_file}")
        
        # 生成config.yaml文件
        config_yaml_file = os.path.join(self.output_dir, "config.yaml")
        config_data = {
            'inventory': {
                'plugin': 'SimpleInventory',
                'options': {
                    'host_file': 'hosts.yaml',
                    'group_file': 'groups.yaml',
                    'defaults_file': 'default.yaml'
                }
            },
            'runner': {
                'plugin': 'threaded',
                'options': {
                    'num_workers': 100
                }
            }
        }
        
        with open(config_yaml_file, 'w', encoding='utf-8') as f:
            f.write("---\n")
            yaml.dump(config_data, f, allow_unicode=True, default_flow_style=False, indent=2)
        
        logger.info(f"YAML格式config文件已保存到: {config_yaml_file}")
    
    def _save_network_devices_yaml_inventory(self, inventory, timestamp):
        """保存只包含网络设备的YAML格式inventory文件
        
        Args:
            inventory (dict): 要保存的inventory字典
            timestamp (str): 时间戳
        """
        # 获取网络设备类型列表
        network_device_types = DEVICE_MAPPING_CONFIG.get('network_device_types', [
            'cisco_ios', 'cisco_nxos', 'huawei_vrp', 'juniper_junos', 
            'juniper_screenos', 'hp_procurve', 'hp_comware'
        ])
        
        # 映射设备类型到正确的platform
        platform_mapping = {
            'cisco_ios': 'cisco_ios',
            'cisco_nxos': 'cisco_nxos',
            'huawei': 'huawei_vrp',
            'huawei_vrp': 'huawei_vrp',
            'junos': 'juniper_junos',
            'juniper_junos': 'juniper_junos',
            'juniper_screenos': 'juniper_screenos',
            'hp_procurve': 'hp_procurve',
            'hp_comware': 'hp_comware',
            'linux': 'linux',
            'windows': 'windows',
            'generic_termserver': 'generic_termserver'
        }
        
        # 筛选出网络设备
        network_hosts_data = {}
        
        # 转换数据格式以匹配YAML格式，只包含网络设备
        for host, data in inventory['all']['hosts'].items():
            # 根据设备类型确定platform
            platform = data['device_type']
            
            # 只处理网络设备
            if platform in network_device_types:
                # 如果有映射则使用映射值，否则使用原始值
                if platform in platform_mapping:
                    platform = platform_mapping[platform]
                
                network_hosts_data[host] = {
                    'groups': ['dev_group'],  # 默认分组
                    'hostname': data['ansible_host'],
                    'platform': platform
                }
        
        if network_hosts_data:
            # 根据IP地址网段自动分配组
            self._auto_group_hosts_by_network(network_hosts_data)
            
            # 生成只包含网络设备的hosts.yaml文件
            network_hosts_yaml_file = os.path.join(self.output_dir, "network_hosts.yaml")
            with open(network_hosts_yaml_file, 'w', encoding='utf-8') as f:
                yaml.dump(network_hosts_data, f, allow_unicode=True, default_flow_style=False, indent=2)
            
            logger.info(f"YAML格式网络设备hosts文件已保存到: {network_hosts_yaml_file}")
            
            # 生成只包含网络设备的groups.yaml文件
            network_groups_yaml_file = os.path.join(self.output_dir, "network_groups.yaml")
            network_groups_data = {
                'dev_group': {
                    'username': 'esunny',
                    'password': 'Bwxsgdj@2022'
                }
            }
            
            # 添加网络设备类型特定的组
            for host, data in inventory['all']['hosts'].items():
                if data['device_type'] in network_device_types:
                    group_name = data['device_type']
                    if group_name not in network_groups_data:
                        network_groups_data[group_name] = {
                            'platform': group_name if group_name in platform_mapping else group_name
                        }
            
            # 添加网络分组
            self._add_network_groups(network_groups_data, network_hosts_data)
            
            with open(network_groups_yaml_file, 'w', encoding='utf-8') as f:
                f.write("---\n")
                yaml.dump(network_groups_data, f, allow_unicode=True, default_flow_style=False, indent=2)
            
            logger.info(f"YAML格式网络设备groups文件已保存到: {network_groups_yaml_file}")
            
            # 生成只包含网络设备的default.yaml文件
            network_default_yaml_file = os.path.join(self.output_dir, "network_default.yaml")
            default_data = {
                'username': '',
                'password': 'python',
                'platform': 'unknown',
                'connection_options': {
                    'netmiko': {
                        'extras': {
                            'secret': 'esunnytrunk'
                        }
                    }
                }
            }
            
            with open(network_default_yaml_file, 'w', encoding='utf-8') as f:
                f.write("---\n")
                yaml.dump(default_data, f, allow_unicode=True, default_flow_style=False, indent=2)
            
            logger.info(f"YAML格式网络设备default文件已保存到: {network_default_yaml_file}")
    
    def _auto_group_hosts_by_network(self, hosts_data):
        """根据IP地址网段自动分配组
        
        Args:
            hosts_data (dict): 主机数据字典
        """
        # 从配置文件读取网段和组名映射
        network_group_mapping = DEVICE_MAPPING_CONFIG.get('network_group_mapping', {})
        
        import ipaddress
        
        # 检查IP是否在指定网段内
        def ip_in_network(ip, network):
            try:
                ip_obj = ipaddress.ip_address(ip)
                net_obj = ipaddress.ip_network(network, strict=False)
                return ip_obj in net_obj
            except ValueError:
                return False
        
        # 按照网络前缀长度排序，最长前缀优先
        sorted_networks = sorted(
            network_group_mapping.items(), 
            key=lambda x: ipaddress.ip_network(x[0], strict=False).prefixlen, 
            reverse=True
        )
        
        # 遍历所有主机，根据IP地址分配组
        for host_name, host_info in hosts_data.items():
            ip_address = host_info.get('hostname')
            if ip_address:
                # 检查IP地址是否匹配任何定义的网段，按最长前缀优先原则
                for network, group_name in sorted_networks:
                    if ip_in_network(ip_address, network):
                        # 添加网段组到主机
                        if group_name not in host_info['groups']:
                            host_info['groups'].append(group_name)
                        break  # 找到最匹配的网段后停止检查
    
    def _add_network_groups(self, groups_data, hosts_data):
        """添加网络分组定义
        
        Args:
            groups_data (dict): 组数据字典
            hosts_data (dict): 主机数据字典
        """
        # 收集所有网络分组名称
        network_groups = set()
        for host_info in hosts_data.values():
            for group in host_info.get('groups', []):
                if group != 'dev_group' and not group in groups_data:
                    network_groups.add(group)
        
        # 为每个网络分组添加定义
        for group_name in network_groups:
            groups_data[group_name] = {
                'platform': 'generic_termserver'  # 默认平台
            }
    
    def run(self):
        """运行转换流程"""
        try:
            logger.info(f"开始转换Excel文件到Inventory: {self.excel_path}")
            
            # 1. 读取Excel文件
            df = self.read_excel_file()
            
            # 2. 识别主机配置列
            column_mapping = self.identify_host_columns(df)
            
            # 3. 生成inventory
            inventory = self.generate_inventory(df, column_mapping)
            
            # 4. 保存inventory文件
            inventory_file, simple_file, ini_file = self.save_inventory(inventory)
            
            logger.info("转换完成！")
            return inventory_file, simple_file
            
        except Exception as e:
            logger.error(f"转换过程中出错: {str(e)}")
            raise

if __name__ == "__main__":
    # 输入Excel文件路径
    excel_file = "e:/Development/Python/NetOps/data/input/zabbix_host_configs.xlsx"
    
    # 输出目录
    output_dir = "e:/Development/Python/NetOps/data/output/inventory"
    
    # 创建转换器并运行
    converter = ExcelToInventoryConverter(excel_file, output_dir)
    converter.run()