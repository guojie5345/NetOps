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
from src.core.config_manager import ConfigManager

def create_test_config():
    """创建测试配置文件"""
    # 创建SSH配置
    ssh_config = {
        "ssh_devices": [
            {
                "device_type": "cisco_ios",
                "host": "192.168.80.21",
                "username": "nms",
                "password": "cisco",
                "port": 22
            },
            {
                "device_type": "cisco_ios",
                "host": "192.168.80.22",
                "username": "nms",
                "password": "cisco1",
                "port": 22
            }
        ]
    }
    
    # 保存SSH配置到文件
    ssh_config_path = os.path.join(base_dir, 'test_ssh_config.json')
    with open(ssh_config_path, 'w', encoding='utf-8') as f:
        json.dump(ssh_config, f, ensure_ascii=False, indent=2)
        print(f"测试SSH配置文件已创建: {ssh_config_path}")
    
    return ssh_config_path

def test_collect_all():
    """测试collect_all函数"""
    print("开始测试信息采集功能...")
    
    # 创建测试配置
    ssh_config_path = create_test_config()
    
    # 使用ConfigManager加载配置
    config_manager = ConfigManager(ssh_config_path=ssh_config_path)
    config = config_manager.load_config()
    
    try:
        # 调用采集函数
        collect_all(config)
        print("信息采集测试完成")
    except Exception as e:
        print(f"信息采集测试失败: {str(e)}")
    finally:
        # 不再自动删除配置文件，而是提示用户
        print(f"测试SSH配置文件已保留: {ssh_config_path}")
        print("如需删除配置文件，请手动执行删除操作。")

if __name__ == '__main__':
    test_collect_all()