#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API信息采集器

该模块提供通过API接口采集信息的功能。
"""

import json
import logging
import requests
from typing import Dict, Any, Optional
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from src.utils.logger import get_module_logger

# 获取模块日志器
logger = get_module_logger(__name__)


class APICollector:
    """API信息采集器类
    
    该类提供通过HTTP/HTTPS API接口采集信息的功能。
    """
    
    def __init__(self, base_url: str, api_key: Optional[str] = None, timeout: int = 30):
        """初始化API信息采集器
        
        Args:
            base_url (str): API基础URL
            api_key (Optional[str]): API密钥（可选）
            timeout (int): 请求超时时间（秒），默认30秒
        """
        self.base_url = base_url.rstrip('/')  # 移除末尾的斜杠
        self.api_key = api_key
        self.timeout = timeout
        
        # 创建会话对象
        self.session = requests.Session()
        
        # 设置重试策略
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # 设置默认请求头
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "NetOps-APICollector/1.0"
        })
        
        # 如果提供了API密钥，添加到请求头
        if self.api_key:
            self.session.headers.update({
                "Authorization": f"Bearer {self.api_key}"
            })
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[requests.Response]:
        """发起HTTP请求
        
        Args:
            method (str): HTTP方法（GET, POST, PUT, DELETE等）
            endpoint (str): API端点
            **kwargs: 其他传递给requests的参数
            
        Returns:
            Optional[requests.Response]: 响应对象，失败返回None
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        # 设置超时
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
            
        try:
            logger.info(f"发起 {method} 请求到 {url}")
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()  # 抛出HTTP错误
            logger.info(f"请求成功，状态码: {response.status_code}")
            return response
        except requests.exceptions.Timeout:
            logger.error(f"请求超时: {url}")
            return None
        except requests.exceptions.ConnectionError:
            logger.error(f"连接错误: {url}")
            return None
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP错误: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"请求发生未知错误: {str(e)}")
            return None
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """发起GET请求
        
        Args:
            endpoint (str): API端点
            params (Optional[Dict]): 查询参数
            
        Returns:
            Optional[Dict[str, Any]]: 解析后的JSON响应，失败返回None
        """
        response = self._make_request('GET', endpoint, params=params)
        if response:
            try:
                return response.json()
            except json.JSONDecodeError:
                logger.error("响应不是有效的JSON格式")
                return None
        return None
    
    def post(self, endpoint: str, data: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """发起POST请求
        
        Args:
            endpoint (str): API端点
            data (Optional[Dict]): 请求数据
            
        Returns:
            Optional[Dict[str, Any]]: 解析后的JSON响应，失败返回None
        """
        response = self._make_request('POST', endpoint, json=data)
        if response:
            try:
                return response.json()
            except json.JSONDecodeError:
                logger.error("响应不是有效的JSON格式")
                return None
        return None
    
    def put(self, endpoint: str, data: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """发起PUT请求
        
        Args:
            endpoint (str): API端点
            data (Optional[Dict]): 请求数据
            
        Returns:
            Optional[Dict[str, Any]]: 解析后的JSON响应，失败返回None
        """
        response = self._make_request('PUT', endpoint, json=data)
        if response:
            try:
                return response.json()
            except json.JSONDecodeError:
                logger.error("响应不是有效的JSON格式")
                return None
        return None
    
    def delete(self, endpoint: str) -> bool:
        """发起DELETE请求
        
        Args:
            endpoint (str): API端点
            
        Returns:
            bool: 请求成功返回True，失败返回False
        """
        response = self._make_request('DELETE', endpoint)
        return response is not None
    
    def collect_resource_info(self, resource_type: str, resource_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """采集资源信息
        
        Args:
            resource_type (str): 资源类型（如'servers', 'networks', 'volumes'等）
            resource_id (Optional[str]): 资源ID（可选，如果提供则获取特定资源信息）
            
        Returns:
            Optional[Dict[str, Any]]: 资源信息，失败返回None
        """
        try:
            if resource_id:
                endpoint = f"{resource_type}/{resource_id}"
            else:
                endpoint = resource_type
                
            logger.info(f"采集 {resource_type} 资源信息")
            data = self.get(endpoint)
            return data
        except Exception as e:
            logger.error(f"采集资源信息时发生错误: {str(e)}")
            return None
    
    def collect_resources_list(self, resource_type: str) -> Optional[Dict[str, Any]]:
        """采集资源列表
        
        Args:
            resource_type (str): 资源类型（如'servers', 'networks', 'volumes'等）
            
        Returns:
            Optional[Dict[str, Any]]: 资源列表，失败返回None
        """
        return self.collect_resource_info(resource_type)
    
    def collect_server_info(self, server_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """采集服务器信息
        
        Args:
            server_id (Optional[str]): 服务器ID（可选，如果提供则获取特定服务器信息）
            
        Returns:
            Optional[Dict[str, Any]]: 服务器信息，失败返回None
        """
        return self.collect_resource_info('servers', server_id)
    
    def collect_network_info(self, network_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """采集网络信息
        
        Args:
            network_id (Optional[str]): 网络ID（可选，如果提供则获取特定网络信息）
            
        Returns:
            Optional[Dict[str, Any]]: 网络信息，失败返回None
        """
        return self.collect_resource_info('networks', network_id)
    
    def collect_volume_info(self, volume_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """采集存储卷信息
        
        Args:
            volume_id (Optional[str]): 存储卷ID（可选，如果提供则获取特定存储卷信息）
            
        Returns:
            Optional[Dict[str, Any]]: 存储卷信息，失败返回None
        """
        return self.collect_resource_info('volumes', volume_id)


def collect_api_info(base_url: str, api_key: Optional[str] = None, resource_types: list = None) -> Dict[str, Any]:
    """采集API信息的便捷函数
    
    Args:
        base_url (str): API基础URL
        api_key (Optional[str]): API密钥（可选）
        resource_types (list): 要采集的资源类型列表（如['servers', 'networks', 'volumes']）
        
    Returns:
        Dict[str, Any]: 采集到的API信息
    """
    if resource_types is None:
        resource_types = ['servers', 'networks', 'volumes']
    
    collector = APICollector(base_url, api_key)
    api_data = {}
    
    for resource_type in resource_types:
        logger.info(f"开始采集 {resource_type} 资源信息")
        data = collector.collect_resources_list(resource_type)
        if data:
            api_data[resource_type] = data
        else:
            logger.warning(f"采集 {resource_type} 资源信息失败")
    
    return api_data