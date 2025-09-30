#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
采集功能调试测试文件
用于详细测试和调试SSH和API采集功能的各个组件
"""

import os
import sys
import json
import time
import logging
import pytest
from typing import Dict, Any, List, Optional

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入采集模块
from src.modules.collection.ssh_collector import SSHCollector
from src.modules.collection.api_collector import APICollector
from src.modules.collection.collector import collect_all
from src.utils.logger import setup_logger
from src.core.config_manager import ConfigManager

# 设置调试日志
setup_logger()
logger = logging.getLogger(__name__)
# 设置为DEBUG级别
logger.setLevel(logging.DEBUG)
# 确保根logger也设置为DEBUG级别
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)


class TestCollectionDebug:
    """采集功能调试测试类"""
    
    def setup_method(self):
        """测试前的设置"""
        logger.info("开始采集功能调试测试...")
        # 加载测试配置
        self.test_config = self._load_test_config()
        # 创建临时输出目录
        self.output_dir = os.path.join("data", "output", "debug_test")
        os.makedirs(self.output_dir, exist_ok=True)
        logger.info(f"调试输出目录: {self.output_dir}")
    
    def teardown_method(self):
        """测试后的清理"""
        logger.info("采集功能调试测试完成")
    
    def _load_test_config(self) -> Dict[str, Any]:
        """
        加载测试配置
        """
        # 从示例配置文件加载
        example_config_path = os.path.join(
            "src", "modules", "collection", "config_example.json"
        )
        
        try:
            with open(example_config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.info(f"已加载示例配置: {example_config_path}")
            return config
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}")
            # 返回默认配置
            return {
                "ssh_devices": [
                    {
                        "hostname": "192.168.1.1",
                        "device_type": "huawei",
                        "username": "admin",
                        "password": "password",
                        "port": 22,
                        "timeout": 30
                    }
                ],
                "api_endpoints": [
                    {
                        "name": "test_api",
                        "url": "http://127.0.0.1:8000/api/test",
                        "method": "GET",
                        "headers": {"Content-Type": "application/json"},
                        "params": {},
                        "auth": None
                    }
                ]
            }
    
    def test_ssh_collector_connectivity(self):
        """
        测试SSH采集器的连接功能
        """
        logger.info("=== 测试SSH采集器连接功能 ===")
        results = {}
        
        for device in self.test_config.get("ssh_devices", []):
            # 转换设备信息格式，适配SSHCollector
            device_info = device.copy()
            if 'hostname' in device_info and 'host' not in device_info:
                device_info['host'] = device_info.pop('hostname')
            
            device_name = device_info.get('host', 'Unknown')
            logger.info(f"测试设备连接: {device_name} ({device_info.get('device_type', 'Unknown')})")
            collector = SSHCollector(device_info=device_info)
            
            try:
                # 测试连接
                start_time = time.time()
                connected = collector.connect()
                connect_time = time.time() - start_time
                
                results[device_name] = {
                    "connected": connected,
                    "connect_time": connect_time,
                    "error": None
                }
                
                if connected:
                    logger.info(f"✅ 成功连接到 {device_name}，耗时: {connect_time:.2f}秒")
                    # 执行简单命令测试
                    response = collector.execute_command("display version")
                    logger.debug(f"版本信息命令输出长度: {len(response)} 字符")
                    collector.disconnect()
                else:
                    logger.error(f"❌ 连接 {device_name} 失败")
                    
            except Exception as e:
                error_msg = str(e)
                logger.error(f"❌ 测试 {device_name} 时出现异常: {error_msg}")
                results[device_name] = {
                    "connected": False,
                    "connect_time": 0,
                    "error": error_msg
                }
                
        # 保存结果
        self._save_results("ssh_connectivity_test.json", results)
        return results
    
    def test_api_collector_endpoints(self):
        """
        测试API采集器的端点连接和响应
        """
        logger.info("=== 测试API采集器端点功能 ===")
        results = {}
        
        for endpoint in self.test_config.get("api_endpoints", []):
            endpoint_name = endpoint.get("name", endpoint["url"])
            logger.info(f"测试API端点: {endpoint_name}")
            
            try:
                # 测试API调用
                collector = APICollector()
                start_time = time.time()
                response = collector.collect_api_data(endpoint)
                response_time = time.time() - start_time
                
                results[endpoint_name] = {
                    "status": response.get("status_code", "N/A"),
                    "response_time": response_time,
                    "data_size": len(str(response.get("data", ""))),
                    "error": None
                }
                
                logger.info(f"API调用结果 - {endpoint_name}: 状态码 {response.get('status_code')}, "
                           f"响应时间: {response_time:.2f}秒, 数据大小: {results[endpoint_name]['data_size']} 字符")
                
            except Exception as e:
                error_msg = str(e)
                logger.error(f"❌ 测试API端点 {endpoint_name} 时出现异常: {error_msg}")
                results[endpoint_name] = {
                    "status": "ERROR",
                    "response_time": 0,
                    "data_size": 0,
                    "error": error_msg
                }
        
        # 保存结果
        self._save_results("api_endpoints_test.json", results)
        return results
    
    def test_ssh_command_execution(self):
        """
        测试SSH命令执行功能
        """
        logger.info("=== 测试SSH命令执行功能 ===")
        results = {}
        
        # 要测试的命令列表
        commands_to_test = [
            "display version",
            "display interface brief",
            "display ip routing-table",
            "display device"
        ]
        
        for device in self.test_config.get("ssh_devices", []):
            # 转换设备信息格式，适配SSHCollector
            device_info = device.copy()
            if 'hostname' in device_info and 'host' not in device_info:
                device_info['host'] = device_info.pop('hostname')
            
            device_name = device_info.get('host', 'Unknown')
            logger.info(f"在设备 {device_name} 上测试命令执行")
            collector = SSHCollector(device_info=device_info)
            device_results = {}
            
            try:
                if collector.connect():
                    for cmd in commands_to_test:
                        try:
                            start_time = time.time()
                            output = collector.execute_command(cmd)
                            exec_time = time.time() - start_time
                            
                            device_results[cmd] = {
                                "success": True,
                                "execution_time": exec_time,
                                "output_length": len(output),
                                "output_sample": output[:100] + "..." if len(output) > 100 else output,
                                "error": None
                            }
                            logger.info(f"✅ 命令 '{cmd}' 执行成功，耗时: {exec_time:.2f}秒, 输出长度: {len(output)} 字符")
                            
                        except Exception as e:
                            error_msg = str(e)
                            logger.error(f"❌ 命令 '{cmd}' 执行失败: {error_msg}")
                            device_results[cmd] = {
                                "success": False,
                                "execution_time": 0,
                                "output_length": 0,
                                "output_sample": "",
                                "error": error_msg
                            }
                    
                    collector.disconnect()
                else:
                    logger.error(f"❌ 无法连接到设备 {device_name}")
                    device_results["connection"] = "failed"
                    
            except Exception as e:
                logger.error(f"❌ 测试设备 {device_name} 时出现异常: {str(e)}")
                device_results["error"] = str(e)
            
            results[device_name] = device_results
        
        # 保存结果
        self._save_results("ssh_commands_test.json", results)
        return results
    
    def test_collect_all_function(self):
        """
        测试collect_all函数的完整功能
        """
        logger.info("=== 测试collect_all函数完整功能 ===")
        
        try:
            # 使用测试配置
            config = {
                "collection": self.test_config,
                "output": {
                    "directory": self.output_dir,
                    "format": "json"
                }
            }
            
            # 测试完整的采集流程
            start_time = time.time()
            all_results = collect_all(config)
            total_time = time.time() - start_time
            
            logger.info(f"✅ 完整采集流程执行成功，总耗时: {total_time:.2f}秒")
            logger.info(f"采集结果概览: SSH设备数={len(all_results.get('ssh_results', []))}, "
                       f"API端点数={len(all_results.get('api_results', []))}")
            
            # 保存结果
            self._save_results("collect_all_test.json", all_results)
            
            return all_results
            
        except Exception as e:
            logger.error(f"❌ 执行collect_all函数时出现异常: {str(e)}")
            # 保存错误信息
            error_info = {
                "error": str(e),
                "exception_type": type(e).__name__
            }
            self._save_results("collect_all_error.json", error_info)
            return error_info
    
    def _save_results(self, filename: str, data: Any):
        """
        保存测试结果到文件
        """
        file_path = os.path.join(self.output_dir, filename)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"测试结果已保存到: {file_path}")
        except Exception as e:
            logger.error(f"保存测试结果失败: {str(e)}")
    
    def test_config_validation(self):
        """
        测试配置验证功能
        """
        logger.info("=== 测试配置验证功能 ===")
        
        # 测试不同类型的配置
        test_cases = [
            {
                "name": "有效配置",
                "config": self.test_config
            },
            {
                "name": "缺少SSH设备配置",
                "config": {"api_endpoints": self.test_config.get("api_endpoints", [])}
            },
            {
                "name": "缺少API端点配置",
                "config": {"ssh_devices": self.test_config.get("ssh_devices", [])}
            },
            {
                "name": "空配置",
                "config": {}
            },
            {
                "name": "不完整的设备配置",
                "config": {
                    "ssh_devices": [
                        {"hostname": "192.168.1.1"}  # 缺少必要字段
                    ]
                }
            }
        ]
        
        results = {}
        
        for test_case in test_cases:
            logger.info(f"测试配置: {test_case['name']}")
            
            try:
                # 尝试使用配置创建采集器
                if "ssh_devices" in test_case["config"]:
                    for device in test_case["config"]["ssh_devices"]:
                        try:
                            # 转换设备信息格式，适配SSHCollector
                            device_info = device.copy()
                            if 'hostname' in device_info and 'host' not in device_info:
                                device_info['host'] = device_info.pop('hostname')
                            
                            collector = SSHCollector(device_info=device_info)
                            logger.info(f"✅ 设备配置验证通过: {device_info.get('host', 'unknown')}")
                        except TypeError as e:
                            logger.warning(f"⚠️  设备配置不完整: {str(e)}")
                
                results[test_case["name"]] = "success"
                
            except Exception as e:
                logger.error(f"❌ 配置 '{test_case['name']}' 验证失败: {str(e)}")
                results[test_case["name"]] = f"error: {str(e)}"
        
        # 保存结果
        self._save_results("config_validation_test.json", results)
        return results


def run_individual_test(test_name: str):
    """
    运行单个测试方法
    
    Args:
        test_name: 测试方法名
    """
    logger.info(f"运行单个测试: {test_name}")
    test_instance = TestCollectionDebug()
    test_instance.setup_method()
    
    try:
        if hasattr(test_instance, test_name):
            test_method = getattr(test_instance, test_name)
            result = test_method()
            logger.info(f"测试 {test_name} 完成")
            return result
        else:
            logger.error(f"测试方法 {test_name} 不存在")
            return None
    finally:
        test_instance.teardown_method()


def run_all_tests():
    """
    运行所有测试
    """
    logger.info("运行所有采集功能调试测试")
    test_instance = TestCollectionDebug()
    test_instance.setup_method()
    
    results = {
        "ssh_connectivity": test_instance.test_ssh_collector_connectivity(),
        "api_endpoints": test_instance.test_api_collector_endpoints(),
        "ssh_commands": test_instance.test_ssh_command_execution(),
        "config_validation": test_instance.test_config_validation(),
        "collect_all": test_instance.test_collect_all_function()
    }
    
    test_instance.teardown_method()
    
    # 保存总体结果
    summary_path = os.path.join(test_instance.output_dir, "test_summary.json")
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    logger.info(f"所有测试完成，总结已保存到: {summary_path}")
    return results


if __name__ == "__main__":
    # 命令行参数处理
    if len(sys.argv) > 1:
        # 运行指定的测试
        test_method = sys.argv[1]
        if test_method.startswith("test_"):
            run_individual_test(test_method)
        elif test_method == "all":
            run_all_tests()
        else:
            print(f"未知的测试方法: {test_method}")
            print("使用方法:")
            print("  python debug_collection.py all           # 运行所有测试")
            print("  python debug_collection.py test_ssh_collector_connectivity  # 运行指定测试")
    else:
        # 运行交互式菜单
        print("=== 采集功能调试工具 ===")
        print("请选择要运行的测试:")
        print("1. 测试SSH连接功能")
        print("2. 测试API端点功能")
        print("3. 测试SSH命令执行")
        print("4. 测试配置验证")
        print("5. 测试完整采集流程")
        print("6. 运行所有测试")
        
        choice = input("请输入选择 (1-6): ")
        
        test_map = {
            "1": "test_ssh_collector_connectivity",
            "2": "test_api_collector_endpoints",
            "3": "test_ssh_command_execution",
            "4": "test_config_validation",
            "5": "test_collect_all_function",
            "6": "all"
        }
        
        if choice in test_map:
            if choice == "6":
                run_all_tests()
            else:
                run_individual_test(test_map[choice])
        else:
            print("无效的选择")