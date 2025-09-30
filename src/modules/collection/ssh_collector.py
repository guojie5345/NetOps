#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SSH信息采集器

该模块提供通过SSH连接网络设备并采集信息的功能。
"""

import json
import logging
from typing import Dict, Any, List, Optional
from netmiko import ConnectHandler, NetMikoTimeoutException, NetMikoAuthenticationException
from paramiko.ssh_exception import SSHException

from src.utils.logger import get_module_logger

# 获取模块日志器
logger = get_module_logger(__name__)


class SSHCollector:
    """SSH信息采集器类
    
    该类提供通过SSH连接网络设备并执行命令来采集设备信息的功能。
    """
    
    def __init__(self, device_info: Dict[str, Any]):
        """初始化SSH信息采集器
        
        Args:
            device_info (Dict[str, Any]): 设备连接信息，包含以下键：
                - device_type: 设备类型（如'cisco_ios', 'huawei', 'hp_comware'等）
                - host: 设备IP地址
                - username: 用户名
                - password: 密码
                - port: 端口号（可选，默认22）
                - secret: 特权密码（可选）
        """
        self.device_info = device_info
        self.connection = None
        self.is_connected = False
        
    def connect(self) -> bool:
        """建立SSH连接
        
        Returns:
            bool: 连接成功返回True，失败返回False
        """
        try:
            logger.info(f"正在连接设备 {self.device_info.get('host', 'Unknown')}")
            self.connection = ConnectHandler(**self.device_info)
            self.is_connected = True
            logger.info(f"成功连接到设备 {self.device_info.get('host', 'Unknown')}")
            return True
        except NetMikoTimeoutException:
            logger.error(f"连接设备 {self.device_info.get('host', 'Unknown')} 超时")
            return False
        except NetMikoAuthenticationException:
            logger.error(f"连接设备 {self.device_info.get('host', 'Unknown')} 认证失败")
            return False
        except SSHException as e:
            logger.error(f"连接设备 {self.device_info.get('host', 'Unknown')} 时发生SSH错误: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"连接设备 {self.device_info.get('host', 'Unknown')} 时发生未知错误: {str(e)}")
            return False
    
    def disconnect(self) -> None:
        """断开SSH连接"""
        if self.connection and self.is_connected:
            try:
                self.connection.disconnect()
                self.is_connected = False
                logger.info(f"已断开与设备 {self.device_info.get('host', 'Unknown')} 的连接")
            except Exception as e:
                logger.error(f"断开设备连接时发生错误: {str(e)}")
    
    def execute_command(self, command: str, use_textfsm: bool = False) -> Optional[str]:
        """执行单个命令
        
        Args:
            command (str): 要执行的命令
            use_textfsm (bool): 是否使用textfsm解析输出
            
        Returns:
            Optional[str]: 命令执行结果，失败返回None
        """
        if not self.is_connected:
            logger.error("设备未连接，无法执行命令")
            return None
            
        try:
            logger.info(f"在设备 {self.device_info.get('host', 'Unknown')} 上执行命令: {command}")
            output = self.connection.send_command(command, use_textfsm=use_textfsm)
            logger.debug(f"命令执行结果: {output}")
            return output
        except Exception as e:
            logger.error(f"执行命令 '{command}' 时发生错误: {str(e)}")
            return None
    
    def execute_commands(self, commands: List[str]) -> Dict[str, Optional[str]]:
        """执行多个命令
        
        Args:
            commands (List[str]): 要执行的命令列表
            
        Returns:
            Dict[str, Optional[str]]: 命令执行结果字典，键为命令，值为执行结果
        """
        results = {}
        for command in commands:
            results[command] = self.execute_command(command)
        return results
    
    def collect_basic_info(self) -> Dict[str, Any]:
        """采集设备基本信息
        
        Returns:
            Dict[str, Any]: 设备基本信息字典
        """
        if not self.is_connected:
            logger.error("设备未连接，无法采集信息")
            return {}
        
        basic_info = {
            'host': self.device_info.get('host', ''),
            'device_type': self.device_info.get('device_type', ''),
        }
        
        # 根据设备类型执行不同的命令
        device_type = self.device_info.get('device_type', '')
        
        if 'cisco' in device_type:
            commands = [
                'show version',
                'show running-config',
                'show ip interface brief',
                'show vlan brief'
            ]
        elif 'huawei' in device_type or 'hp_comware' in device_type:
            commands = [
                'display version',
                'display current-configuration',
                'display ip interface brief',
                'display vlan brief'
            ]
        else:
            # 默认命令
            commands = [
                'show version'
            ]
        
        # 执行命令并收集结果
        command_results = self.execute_commands(commands)
        basic_info.update(command_results)
        
        return basic_info
    
    def collect_interface_info(self) -> Dict[str, Any]:
        """采集设备接口信息
        
        Returns:
            Dict[str, Any]: 设备接口信息字典
        """
        if not self.is_connected:
            logger.error("设备未连接，无法采集接口信息")
            return {}
        
        interface_info = {
            'host': self.device_info.get('host', ''),
            'device_type': self.device_info.get('device_type', ''),
        }
        
        # 根据设备类型执行不同的命令
        device_type = self.device_info.get('device_type', '')
        
        if 'cisco' in device_type:
            command = 'show interfaces'
        elif 'huawei' in device_type or 'hp_comware' in device_type:
            command = 'display interface'
        else:
            # 默认命令
            command = 'show interfaces'
        
        # 执行命令并收集结果
        result = self.execute_command(command)
        interface_info['interfaces'] = result
        
        return interface_info
    
    def collect_arp_info(self) -> Dict[str, Any]:
        """采集设备ARP表信息
        
        Returns:
            Dict[str, Any]: 设备ARP表信息字典
        """
        if not self.is_connected:
            logger.error("设备未连接，无法采集ARP信息")
            return {}
        
        arp_info = {
            'host': self.device_info.get('host', ''),
            'device_type': self.device_info.get('device_type', ''),
        }
        
        # 根据设备类型执行不同的命令
        device_type = self.device_info.get('device_type', '')
        
        if 'cisco' in device_type:
            command = 'show arp'
        elif 'huawei' in device_type or 'hp_comware' in device_type:
            command = 'display arp'
        else:
            # 默认命令
            command = 'show arp'
        
        # 执行命令并收集结果
        result = self.execute_command(command)
        arp_info['arp_table'] = result
        
        return arp_info


def collect_device_info(device_info: Dict[str, Any]) -> Dict[str, Any]:
    """采集单个设备信息的便捷函数
    
    Args:
        device_info (Dict[str, Any]): 设备连接信息
        
    Returns:
        Dict[str, Any]: 设备采集到的信息
    """
    collector = SSHCollector(device_info)
    
    # 尝试连接设备
    if not collector.connect():
        logger.error(f"无法连接到设备 {device_info.get('host', 'Unknown')}")
        return {}
    
    try:
        # 采集设备基本信息
        basic_info = collector.collect_basic_info()
        
        # 采集接口信息
        interface_info = collector.collect_interface_info()
        
        # 采集ARP表信息
        arp_info = collector.collect_arp_info()
        
        # 合并所有信息
        device_data = {}
        device_data.update(basic_info)
        device_data.update(interface_info)
        device_data.update(arp_info)
        
        return device_data
    finally:
        # 断开连接
        collector.disconnect()