#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API采集器模块

该模块提供通过HTTP/HTTPS API接口采集网络设备信息的功能。
"""

import requests
import json
import logging
from typing import Dict, Any, Optional
from src.utils.logger import get_module_logger

# 设置日志
logger = get_module_logger(__name__)


class APICollector:
    """API采集器类，用于通过API接口采集设备信息"""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None, timeout: int = 30):
        """初始化API采集器
        
        Args:
            base_url: API基础URL
            api_key: API密钥（可选）
            timeout: 请求超时时间（秒）
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()
        
        # 如果提供了API密钥，则设置认证头
        if api_key:
            self.session.headers.update({'Authorization': f'Bearer {api_key}'})

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """发起HTTP请求
        
        Args:
            method: HTTP方法（GET/POST/PUT/DELETE等）
            endpoint: API端点
            **kwargs: 其他请求参数
            
        Returns:
            Optional[Dict[str, Any]]: 响应数据，失败时返回None
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            logger.debug(f"发起 {method} 请求到 {url}")
            
            # 设置默认超时
            if 'timeout' not in kwargs:
                kwargs['timeout'] = self.timeout
                
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()  # 抛出HTTP错误
            
            # 尝试解析JSON响应
            try:
                data = response.json()
                logger.debug(f"请求成功，收到数据: {len(str(data))} 字符")
                return data
            except json.JSONDecodeError:
                # 如果不是JSON格式，返回文本内容
                logger.warning(f"响应不是JSON格式: {response.text[:100]}...")
                return {"text": response.text}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"API请求失败 {url}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"处理API响应时发生错误 {url}: {str(e)}")
            return None

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """发送GET请求
        
        Args:
            endpoint: API端点
            params: 查询参数
            
        Returns:
            Optional[Dict[str, Any]]: 响应数据，失败时返回None
        """
        return self._make_request('GET', endpoint, params=params)

    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """发送POST请求
        
        Args:
            endpoint: API端点
            data: 请求数据
            
        Returns:
            Optional[Dict[str, Any]]: 响应数据，失败时返回None
        """
        headers = {'Content-Type': 'application/json'}
        return self._make_request('POST', endpoint, json=data, headers=headers)

    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """发送PUT请求
        
        Args:
            endpoint: API端点
            data: 请求数据
            
        Returns:
            Optional[Dict[str, Any]]: 响应数据，失败时返回None
        """
        headers = {'Content-Type': 'application/json'}
        return self._make_request('PUT', endpoint, json=data, headers=headers)

    def delete(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """发送DELETE请求
        
        Args:
            endpoint: API端点
            
        Returns:
            Optional[Dict[str, Any]]: 响应数据，失败时返回None
        """
        return self._make_request('DELETE', endpoint)

    def close(self):
        """关闭会话"""
        self.session.close()


def collect_device_info_via_api(base_url: str, api_key: Optional[str], endpoints: list) -> Dict[str, Any]:
    """
    通过API收集设备信息
    
    Args:
        base_url: API基础URL
        api_key: API密钥
        endpoints: 要访问的API端点列表
        
    Returns:
        Dict[str, Any]: 端点到数据的映射
    """
    collector = APICollector(base_url, api_key)
    
    try:
        results = {}
        for endpoint in endpoints:
            data = collector.get(endpoint)
            if data is not None:
                results[endpoint] = data
            else:
                results[endpoint] = f"端点 '{endpoint}' 请求失败"
        return results
    finally:
        collector.close()


if __name__ == "__main__":
    # 示例用法
    api_base_url = "https://api.example.com/v1"
    api_key = "your-api-key-here"
    
    endpoints = [
        "devices",
        "devices/status",
        "interfaces"
    ]
    
    try:
        print("开始通过API收集设备信息...")
        results = collect_device_info_via_api(api_base_url, api_key, endpoints)
        
        for endpoint, data in results.items():
            print(f"\n端点: {endpoint}")
            print(f"数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
    except Exception as e:
        logger.error(f"程序执行失败: {str(e)}")
        print(f"程序执行失败: {str(e)}")