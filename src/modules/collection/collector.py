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
        # 如果没有SSH设备配置，直接返回空字典而不记录日志
        if not self.ssh_devices:
            self.collected_data['ssh'] = {}
            return {}
            
        logger.info("开始采集SSH设备信息")
        ssh_data = {}
        success_count = 0
        failed_count = 0
        
        for device_info in self.ssh_devices:
            host = device_info.get('host', 'Unknown')
            logger.info(f"采集设备 {host} 的信息")
            
            try:
                # 采集单个设备信息
                device_data = collect_device_info(device_info)
                ssh_data[host] = device_data
                
                # 检查是否成功采集到信息（空字典表示连接失败）
                if device_data:  # 如果返回的不是空字典，则认为采集成功
                    success_count += 1
                else:
                    failed_count += 1
                    logger.warning(f"设备 {host} 信息采集失败或返回空数据")
                
            except Exception as e:
                logger.error(f"采集设备 {host} 信息时发生错误: {str(e)}")
                ssh_data[host] = {'error': str(e)}
                failed_count += 1
        
        self.collected_data['ssh'] = ssh_data
        
        # 根据成功和失败的设备数量生成不同的日志信息
        total_devices = len(self.ssh_devices)
        if failed_count == 0:
            logger.info(f"所有 {total_devices} 台设备采集成功")
        elif success_count == 0:
            logger.warning(f"所有 {total_devices} 台设备采集失败")
        else:
            logger.warning(f"成功: {success_count} 台, 失败: {failed_count} 台")
            
        return ssh_data
    
    def collect_api_info(self) -> Dict[str, Any]:
        """采集所有API端点信息
        
        Returns:
            Dict[str, Any]: API端点采集信息
        """
        # 如果没有API端点配置，直接返回空字典而不记录日志
        if not self.api_endpoints:
            self.collected_data['api'] = {}
            return {}
            
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
        # 移除这里的完成日志，因为会在collect_all_info中统一输出
        # logger.info("API端点信息采集完成")
        return api_data
    
    def collect_all_info(self) -> Dict[str, Any]:
        """采集所有信息（SSH和API）
        
        Returns:
            Dict[str, Any]: 所有采集到的信息
        """
        # 检查是否有SSH设备和API端点配置
        has_ssh_devices = bool(self.ssh_devices)
        has_api_endpoints = bool(self.api_endpoints)
        
        # 根据实际配置生成开始采集日志
        if has_ssh_devices and has_api_endpoints:
            logger.info("开始采集所有信息")
        elif has_ssh_devices:
            logger.info("开始采集SSH设备信息")
        elif has_api_endpoints:
            logger.info("开始采集API端点信息")
        else:
            logger.info("没有配置SSH设备和API端点，跳过信息采集")
            self.collected_data['ssh'] = {}
            self.collected_data['api'] = {}
            self.collected_data['timestamp'] = datetime.now().isoformat()
            return self.collected_data
        
        # 采集SSH设备信息（如果有配置）
        self.collect_ssh_info()
        
        # 采集API端点信息（如果有配置）
        self.collect_api_info()
        
        # 添加采集时间戳
        self.collected_data['timestamp'] = datetime.now().isoformat()
        
        # 根据实际采集的信息类型生成更准确的日志
        if has_ssh_devices and has_api_endpoints:
            logger.info("所有信息采集完成")
        elif has_ssh_devices:
            logger.info("SSH设备信息采集完成")
        else:  # 只有API端点
            logger.info("API端点信息采集完成")
            
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