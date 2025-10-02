#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SSH采集器模块

该模块提供通过SSH协议连接网络设备并执行命令的功能，支持多种网络设备平台。
"""

import paramiko
import time
import re
import logging
from typing import Dict, Any, Optional
from src.utils.logger import get_module_logger

# 设置日志
logger = get_module_logger(__name__)


class SSHCollector:
    """SSH采集器类，用于通过SSH连接设备并执行命令"""
    
    def __init__(self, device_info: Dict[str, Any]):
        """初始化SSH采集器
        
        Args:
            device_info: 设备连接信息，包含host, username, password, port, device_type等字段
        """
        self.host = device_info.get('host')
        self.username = device_info.get('username')
        self.password = device_info.get('password')
        self.port = device_info.get('port', 22)
        self.device_type = device_info.get('device_type', 'cisco_ios')
        self.ssh_client = None
        self.shell = None
        # 设置平台特定的命令提示符和延迟时间
        self._setup_platform_config()

    def _setup_platform_config(self):
        """根据设备类型设置平台特定的配置"""
        platform_configs = {
            'cisco_ios': {
                'prompt_pattern': r'[#>$]',
                'delay': 1
            },
            'cisco_nxos': {
                'prompt_pattern': r'[#>$]',
                'delay': 1
            },
            'hp_comware': {
                'prompt_pattern': r'[><\]]',
                'delay': 2
            },
            'huawei_vrp': {
                'prompt_pattern': r'[><\]]',
                'delay': 2
            },
            'juniper_junos': {
                'prompt_pattern': r'[@#>$]',
                'delay': 1
            },
            'juniper_screenos': {
                'prompt_pattern': r'[@#>$]',
                'delay': 1
            }
        }
        
        config = platform_configs.get(self.device_type, platform_configs['cisco_ios'])
        self.prompt_pattern = config['prompt_pattern']
        self.delay = config['delay']

    def connect(self) -> bool:
        """建立SSH连接
        
        Returns:
            bool: 连接是否成功
        """
        try:
            logger.info(f"正在连接到设备 {self.host}:{self.port}")
            
            # 创建SSH客户端
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # 连接设备
            self.ssh_client.connect(
                hostname=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                timeout=10,
                look_for_keys=False,
                allow_agent=False
            )
            
            # 打开交互式shell
            self.shell = self.ssh_client.invoke_shell()
            time.sleep(self.delay)
            
            # 清空初始输出
            self._clear_buffer()
            
            logger.info(f"成功连接到设备 {self.host}")
            return True
            
        except Exception as e:
            logger.error(f"连接到设备 {self.host} 失败: {str(e)}")
            return False

    def _clear_buffer(self):
        """清空SSH缓冲区"""
        if self.shell:
            while self.shell.recv_ready():
                self.shell.recv(65535)

    def _wait_for_prompt(self, timeout: int = 30) -> str:
        """等待命令提示符出现
        
        Args:
            timeout: 超时时间（秒）
            
        Returns:
            str: 收到的输出内容
            
        Raises:
            TimeoutError: 超时时抛出
        """
        output = ""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.shell.recv_ready():
                chunk = self.shell.recv(65535).decode('utf-8', errors='ignore')
                output += chunk
                
                # 检查是否出现提示符
                if re.search(self.prompt_pattern, output.split('\n')[-1]):
                    return output
                    
            time.sleep(0.1)
            
        raise TimeoutError(f"等待命令提示符超时: {self.prompt_pattern}")

    def execute_command(self, command: str, timeout: int = 30) -> Optional[str]:
        """执行命令并获取输出
        
        Args:
            command: 要执行的命令
            timeout: 命令执行超时时间（秒）
            
        Returns:
            Optional[str]: 命令输出，如果执行失败则返回None
        """
        try:
            if not self.shell:
                logger.error("SSH连接未建立")
                return None
                
            logger.debug(f"在设备 {self.host} 上执行命令: {command}")
            
            # 发送命令
            self.shell.send(command + '\n')
            time.sleep(self.delay)
            
            # 等待输出
            output = self._wait_for_prompt(timeout)
            
            # 清理输出，移除命令本身和提示符
            cleaned_output = self._clean_output(output, command)
            
            logger.debug(f"命令 '{command}' 执行完成")
            return cleaned_output
            
        except Exception as e:
            logger.error(f"在设备 {self.host} 上执行命令 '{command}' 失败: {str(e)}")
            return None

    def _clean_output(self, output: str, command: str) -> str:
        """清理命令输出，移除命令本身和提示符
        
        Args:
            output: 原始输出
            command: 执行的命令
            
        Returns:
            str: 清理后的输出
        """
        # 移除命令本身
        lines = output.split('\n')
        # 找到命令行的位置
        command_line_index = -1
        for i, line in enumerate(lines):
            if command in line:
                command_line_index = i
                break
        
        # 如果找到了命令行，从下一行开始截取
        if command_line_index >= 0:
            lines = lines[command_line_index + 1:]
            
        # 移除最后一行的提示符
        if lines and re.search(self.prompt_pattern, lines[-1]):
            lines = lines[:-1]
            
        return '\n'.join(lines).strip()

    def disconnect(self):
        """断开SSH连接"""
        try:
            if self.shell:
                self.shell.close()
            if self.ssh_client:
                self.ssh_client.close()
            logger.info(f"已断开与设备 {self.host} 的连接")
        except Exception as e:
            logger.error(f"断开与设备 {self.host} 的连接时发生错误: {str(e)}")


def collect_device_info(device_info: Dict[str, Any], commands: list) -> Dict[str, Any]:
    """
    收集设备信息
    
    Args:
        device_info: 设备连接信息
        commands: 要执行的命令列表
        
    Returns:
        Dict[str, Any]: 命令到输出的映射
    """
    collector = SSHCollector(device_info)
    
    if not collector.connect():
        return {'error': '连接失败'}
    
    try:
        results = {}
        for command in commands:
            output = collector.execute_command(command)
            if output is not None:
                results[command] = output
            else:
                results[command] = f"命令 '{command}' 执行失败"
        return results
    finally:
        collector.disconnect()


if __name__ == "__main__":
    # 示例用法
    device = {
        "device_type": "cisco_ios",
        "host": "192.168.80.21",
        "username": "nms",
        "password": "cisco",
        "port": 22
    }
    
    commands = [
        "show version",
        "show interfaces status"
    ]
    
    try:
        print("开始收集设备信息...")
        results = collect_device_info(device, commands)
        
        for command, output in results.items():
            print(f"\n命令: {command}")
            print(f"输出:\n{output}")
            
    except Exception as e:
        logger.error(f"程序执行失败: {str(e)}")
        print(f"程序执行失败: {str(e)}")