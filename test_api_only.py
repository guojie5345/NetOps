#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试只有API端点而没有SSH设备的情况
"""

import json
import os
from src.modules.collection.collector import collect_all


def create_api_only_config():
    """创建只包含API端点而不包含SSH设备的配置"""
    config = {
        "api_endpoints": [
            {
                "url": "https://api.example.com",
                "api_key": "test_api_key",
                "resource_types": ["servers", "networks"]
            }
        ]
        # 故意不包含ssh_devices
    }
    
    config_path = "api_only_test_config.json"
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print(f"已创建只包含API端点的测试配置: {config_path}")
    return config_path


def test_api_only_collection():
    """测试只有API端点的采集功能"""
    print("\n开始测试只有API端点而没有SSH设备的情况...")
    
    # 创建测试配置
    config_path = create_api_only_config()
    
    try:
        # 读取配置
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 执行采集
        output_file = "data/output/debug_test/api_only_test.json"
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        print(f"执行信息采集，输出文件: {output_file}")
        data = collect_all(config, output_file)
        
        print("\n采集完成，验证结果:")
        print(f"- 是否包含SSH数据: {'ssh' in data}")
        print(f"- 是否包含API数据: {'api' in data}")
        print("\n测试完成！请检查日志输出，确保没有不必要的SSH相关日志")
        
    finally:
        # 清理测试配置文件
        if os.path.exists(config_path):
            os.remove(config_path)
            print(f"\n已清理测试配置文件: {config_path}")


if __name__ == "__main__":
    test_api_only_collection()