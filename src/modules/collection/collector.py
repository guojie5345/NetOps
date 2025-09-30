#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
信息采集器主类

该模块提供统一的信息采集接口，整合SSH和API采集功能。
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from src.utils.logger import get_module_logger
from .ssh_collector import SSHCollector, collect_device_info
from .api_collector import APICollector, collect_api_info

# 获取模块日志器
logger = get_module_logger(__name__)


class Collector:
    """信息采集器主类
    
    该类提供统一的信息采集接口，整合SSH和API采集功能。
    """
    
    def __init__(self, config: Dict[str, Any]):
        """初始化信息采集器
        
        Args:
            config (Dict[str, Any]): 采集器配置信息，包含以下键：
                - ssh_devices: SSH设备列表，每个设备包含连接信息
                - api_endpoints: API端点列表，每个端点包含URL和认证信息
        """
        self.config = config
        self.ssh_devices = config.get('ssh_devices', [])
        self.api_endpoints = config.get('api_endpoints', [])
        self.collected_data = {}
    
    def collect_ssh_info(self) -> Dict[str, Any]:
        """采集所有SSH设备信息
        
        Returns:
            Dict[str, Any]: SSH设备采集信息
        """
        logger.info("开始采集SSH设备信息")
        ssh_data = {}
        
        for device_info in self.ssh_devices:
            host = device_info.get('host', 'Unknown')
            logger.info(f"采集设备 {host} 的信息")
            
            try:
                # 采集单个设备信息
                device_data = collect_device_info(device_info)
                ssh_data[host] = device_data
            except Exception as e:
                logger.error(f"采集设备 {host} 信息时发生错误: {str(e)}")
                ssh_data[host] = {'error': str(e)}
        
        self.collected_data['ssh'] = ssh_data
        logger.info("SSH设备信息采集完成")
        return ssh_data
    
    def collect_api_info(self) -> Dict[str, Any]:
        """采集所有API端点信息
        
        Returns:
            Dict[str, Any]: API端点采集信息
        """
        logger.info("开始采集API端点信息")
        api_data = {}
        
        for endpoint_info in self.api_endpoints:
            url = endpoint_info.get('url', 'Unknown')
            logger.info(f"采集API端点 {url} 的信息")
            
            try:
                # 获取API采集器配置
                base_url = endpoint_info.get('url', '')
                api_key = endpoint_info.get('api_key')
                resource_types = endpoint_info.get('resource_types', ['servers', 'networks', 'volumes'])
                
                # 采集API信息
                endpoint_data = collect_api_info(base_url, api_key, resource_types)
                api_data[url] = endpoint_data
            except Exception as e:
                logger.error(f"采集API端点 {url} 信息时发生错误: {str(e)}")
                api_data[url] = {'error': str(e)}
        
        self.collected_data['api'] = api_data
        logger.info("API端点信息采集完成")
        return api_data
    
    def collect_all_info(self) -> Dict[str, Any]:
        """采集所有信息（SSH和API）
        
        Returns:
            Dict[str, Any]: 所有采集到的信息
        """
        logger.info("开始采集所有信息")
        
        # 采集SSH设备信息
        self.collect_ssh_info()
        
        # 采集API端点信息
        self.collect_api_info()
        
        # 添加采集时间戳
        self.collected_data['timestamp'] = datetime.now().isoformat()
        
        logger.info("所有信息采集完成")
        return self.collected_data
    
    def save_data(self, file_path: str) -> bool:
        """保存采集到的数据到文件
        
        Args:
            file_path (str): 保存文件路径
            
        Returns:
            bool: 保存成功返回True，失败返回False
        """
        try:
            logger.info(f"保存采集数据到文件: {file_path}")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.collected_data, f, ensure_ascii=False, indent=2)
            logger.info("数据保存成功")
            return True
        except Exception as e:
            logger.error(f"保存数据时发生错误: {str(e)}")
            return False
    
    def get_collected_data(self) -> Dict[str, Any]:
        """获取采集到的数据
        
        Returns:
            Dict[str, Any]: 采集到的数据
        """
        return self.collected_data


def collect_all(config: Dict[str, Any], output_file: Optional[str] = None) -> Dict[str, Any]:
    """采集所有信息的便捷函数
    
    Args:
        config (Dict[str, Any]): 采集器配置信息
        output_file (Optional[str]): 输出文件路径（可选）
        
    Returns:
        Dict[str, Any]: 采集到的所有信息
    """
    collector = Collector(config)
    data = collector.collect_all_info()
    
    # 如果指定了输出文件，保存数据
    if output_file:
        collector.save_data(output_file)
    
    return data