#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""信息采集模块测试脚本"""

import sys
import os
import json

# 获取当前文件所在目录的绝对路径
base_dir = os.path.dirname(os.path.abspath(__file__))
# 添加项目根目录到系统路径
sys.path.insert(0, base_dir)

from src.modules.collection.collector import collect_all

def create_test_config():
    """创建测试配置文件"""
    config = {
        "ssh_devices": [
            {
                "device_type": "huawei",
                "host": "192.168.1.1",
                "username": "testuser",
                "password": "testpass",
                "port": 22
            }
        ],
        "api_endpoints": [
            {
                "name": "测试API",
                "url": "https://httpbin.org/get",
                "method": "GET",
                "headers": {
                    "User-Agent": "NetOps-Tool/1.0"
                }
            }
        ]
    }
    
    # 保存配置到文件
    config_path = os.path.join(base_dir, 'test_collection_config.json')
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    return config_path

def test_collect_all():
    """测试collect_all函数"""
    print("开始测试信息采集功能...")
    
    # 创建测试配置
    config_path = create_test_config()
    
    # 加载配置
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    try:
        # 调用采集函数
        collect_all(config)
        print("信息采集测试完成")
    except Exception as e:
        print(f"信息采集测试失败: {str(e)}")
    finally:
        # 清理测试配置文件
        if os.path.exists(config_path):
            os.remove(config_path)

if __name__ == '__main__':
    test_collect_all()