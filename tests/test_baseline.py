#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
基线检查功能测试脚本

该脚本用于测试基线检查功能，使用SSHCollector代替Nornir执行设备检查。
"""

import json
import os
import sys
import yaml

# 获取当前文件所在目录的绝对路径
base_dir = os.path.dirname(os.path.abspath(__file__))
# 添加项目根目录到系统路径
project_root = os.path.dirname(base_dir)
sys.path.insert(0, project_root)

from src.modules.baseline.check_baseline import check_devices_baseline
from src.utils.logger import setup_logger

# 设置日志
logger = setup_logger("test_baseline")


def load_ssh_config(config_path):
    """
    加载SSH配置文件
    
    Args:
        config_path: SSH配置文件路径
        
    Returns:
        list: 设备列表
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        # 转换为设备列表格式
        devices = []
        # 注意：实际的SSH配置文件使用的是'ssh_devices'键而不是'devices'键
        for device_info in config.get('ssh_devices', []):
            # 映射字段名，确保device_type存在
            device = {
                'device_type': device_info.get('device_type', 'cisco_ios'),
                'host': device_info.get('host'),
                'username': device_info.get('username'),
                'password': device_info.get('password'),
                'port': device_info.get('port', 22)
            }
            # 确保必需字段都存在
            if all(device.get(key) for key in ['host', 'username', 'password']):
                devices.append(device)
            else:
                logger.warning(f"设备配置不完整: {device}")
        return devices
    except Exception as e:
        logger.error(f"加载SSH配置文件失败: {str(e)}")
        return []


def test_baseline():
    """
    测试基线检查功能
    """
    try:
        # 获取当前文件所在目录的绝对路径
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # 定义配置文件路径
        ssh_config_path = os.path.join(current_dir, 'config', 'ssh_config.json')
        rules_file_path = os.path.join(current_dir, 'config', 'baseline_rules.yaml')
        
        # 检查配置文件是否存在
        if not os.path.exists(ssh_config_path):
            logger.error(f"SSH配置文件不存在: {ssh_config_path}")
            # 创建测试配置文件
            test_devices = [
                {
                    "device_type": "cisco_ios",
                    "host": "192.168.80.21",
                    "username": "nms",
                    "password": "cisco",
                    "port": 22
                }
            ]
            # 保存测试配置
            os.makedirs(os.path.dirname(ssh_config_path), exist_ok=True)
            with open(ssh_config_path, 'w', encoding='utf-8') as f:
                json.dump({"devices": test_devices}, f, indent=2, ensure_ascii=False)
            logger.info(f"已创建测试SSH配置文件: {ssh_config_path}")
            devices = test_devices
        else:
            # 加载设备配置
            devices = load_ssh_config(ssh_config_path)
        
        if not devices:
            logger.error("没有可用的设备配置")
            return
        
        # 检查规则文件是否存在
        if not os.path.exists(rules_file_path):
            logger.error(f"基线规则文件不存在: {rules_file_path}")
            # 创建示例规则文件
            example_rules = {
                "common": [
                    {
                        "rule": "service password-encryption",
                        "description": "密码加密服务检查",
                        "regex": False
                    },
                    {
                        "rule": "logging buffered",
                        "description": "日志缓冲区检查",
                        "regex": False
                    }
                ],
                "cisco_ios": [
                    {
                        "rule": "aaa new-model",
                        "description": "AAA认证检查",
                        "regex": False
                    },
                    {
                        "rule": "ip ssh version 2",
                        "description": "SSH版本2检查",
                        "regex": False
                    }
                ]
            }
            # 保存示例规则
            os.makedirs(os.path.dirname(rules_file_path), exist_ok=True)
            with open(rules_file_path, 'w', encoding='utf-8') as f:
                yaml.dump(example_rules, f, default_flow_style=False, allow_unicode=True)
            logger.info(f"已创建示例基线规则文件: {rules_file_path}")
        
        logger.info(f"开始测试基线检查，共 {len(devices)} 台设备")
        
        # 执行基线检查
        results = check_devices_baseline(
            device_list=devices,
            rules_file=rules_file_path,
            max_workers=5
        )
        
        # 统计结果
        success_count = sum(1 for result in results.values() if not result.get('failed', False))
        failed_count = len(results) - success_count
        
        logger.info(f"基线检查测试完成")
        logger.info(f"总设备数: {len(devices)}")
        logger.info(f"成功检查: {success_count}")
        logger.info(f"检查失败: {failed_count}")
        
        # 输出详细结果
        for host, result in results.items():
            if result.get('failed', False):
                logger.error(f"设备 {host} 检查失败: {result.get('error', '未知错误')}")
            else:
                passed_rules = sum(1 for r in result.get('results', []) if r.get('compliant', False))
                total_rules = len(result.get('results', []))
                logger.info(f"设备 {host}: 通过 {passed_rules}/{total_rules} 条规则")
        
        print("\n测试完成！")
        print(f"总设备数: {len(devices)}")
        print(f"成功检查: {success_count}")
        print(f"检查失败: {failed_count}")
        print("\n报告已生成在 reports/ 目录下")
        
    except Exception as e:
        logger.error(f"测试过程中发生错误: {str(e)}", exc_info=True)
        print(f"测试失败: {str(e)}")


if __name__ == "__main__":
    print("开始测试基线检查功能...")
    test_baseline()