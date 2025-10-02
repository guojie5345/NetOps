#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""ITSM变更自动化工具主程序"""

import sys
import os
import argparse
import logging

from src.modules.processing.process_order import OrderProcessor
from src.modules.apis.aliyun_api import AliYunApiClient
from src.utils.logger import setup_logger
from src.core.config_manager import ConfigManager

# from aliyun.ecs.request.v20140526 import DescribeInstancesRequest

# 获取当前文件所在目录的绝对路径
base_dir = os.path.dirname(os.path.abspath(__file__))
# 添加项目根目录到系统路径
sys.path.insert(0, base_dir)

# def get_aliyun_resource_info(aliyun_config):
#     """获取阿里云资源信息"""
#     aliyun_client = AliYunApiClient(
#         region_id=aliyun_config['region_id'],
#         access_key_id=aliyun_config['access_key_id'],
#         access_key_secret=aliyun_config['access_key_secret']
#     )
#     # 调用DescribeInstancesRequest获取实例列表
#     try:
#         request = DescribeInstancesRequest()
#         # 设置请求参数
#         request.set_accept_format('json')
#         # 调用API获取实例列表
#         # response = aliyun_client.client.do_action_with_exception(request)
#         # return json.loads(response)
#         return []  # 临时返回空列表，避免运行错误
#     except Exception as e:
#         logging.error(f'获取阿里云资源信息失败: {str(e)}')
#         return []


# 修改main函数，支持直接调用
def main(config_path=None, ssh_config_path=None, api_config_path=None, order_path=None, action=None):
    """
    主程序入口

    Args:
        config_path (str, optional): 通用配置文件路径. Defaults to None.
        ssh_config_path (str, optional): SSH配置文件路径. Defaults to None.
        api_config_path (str, optional): API配置文件路径. Defaults to None.
        order_path (str, optional): 订单文件路径. Defaults to None.
        action (str, optional): 执行动作: process(处理订单), collect(采集数据), generate(生成配置). Defaults to None.
    """
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='ITSM变更自动化工具')
    parser.add_argument('--config', type=str, default='config/config.json', help='通用配置文件路径')
    parser.add_argument('--ssh-config', type=str, default='config/ssh_config.json', help='SSH配置文件路径')
    parser.add_argument('--api-config', type=str, default='config/api_config.json', help='API配置文件路径')
    parser.add_argument('--order', type=str, help='订单文件路径')
    parser.add_argument('--action', type=str, choices=['process', 'collect', 'generate', 'baseline', 'summary'], default='process',
                        help='执行动作: process(处理订单), collect(采集数据), generate(生成配置), baseline(基线检查), summary(汇总报告)')
    parser.add_argument('--log-level', type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], default='INFO',
                        help='日志级别: DEBUG, INFO, WARNING, ERROR')
    
    # 如果没有提供参数，则使用命令行参数
    if config_path is None and ssh_config_path is None and api_config_path is None and order_path is None and action is None:
        args = parser.parse_args()
        config_path = args.config
        ssh_config_path = args.ssh_config
        api_config_path = args.api_config
        order_path = args.order
        action = args.action
        log_level = getattr(logging, args.log_level.upper())
    # 如果提供了部分参数，则使用提供的参数，其余使用默认值
    elif config_path is None:
        args = parser.parse_args([])
        config_path = args.config
    elif ssh_config_path is None:
        ssh_config_path = 'config/ssh_config.json'
    elif api_config_path is None:
        api_config_path = 'config/api_config.json'
    elif action is None:
        action = 'process'
    else:
        log_level = logging.INFO
    
    # 初始化日志
    logger = setup_logger(level=log_level)
    logger.info('ITSM变更自动化工具启动')

    # 如果没有提供参数，则使用命令行参数
    if config_path is None and ssh_config_path is None and api_config_path is None and order_path is None and action is None:
        args = parser.parse_args()
        config_path = args.config
        ssh_config_path = args.ssh_config
        api_config_path = args.api_config
        order_path = args.order
        action = args.action
    # 如果提供了部分参数，则使用提供的参数，其余使用默认值
    elif config_path is None:
        args = parser.parse_args([])
        config_path = args.config
    elif ssh_config_path is None:
        ssh_config_path = 'config/ssh_config.json'
    elif api_config_path is None:
        api_config_path = 'config/api_config.json'
    elif action is None:
        action = 'process'

    # 加载配置
    config_manager = ConfigManager(
        config_path=config_path,
        ssh_config_path=ssh_config_path,
        api_config_path=api_config_path
    )
    config = config_manager.load_config()
    logger.info('配置加载完成')

    # 根据动作执行不同的功能
    if action == 'collect':
        logger.info('开始信息采集...')
        try:
            # 导入信息采集模块
            from src.modules.collection.collector import collect_all
            
            # 采集信息
            # 注意：这里需要一个配置文件来指定要采集的设备和API端点
            # 示例配置文件可以在 src/modules/collection/config_example.json 找到
            collect_all(config)
            logger.info('信息采集完成')
        except Exception as e:
            logger.error(f'信息采集失败: {str(e)}')
    elif action == 'baseline':
        logger.info('开始基线检查...')
        try:
            # 导入基线检查模块
            from src.modules.baseline.check_baseline import check_devices_baseline
            
            # 获取SSH设备配置
            ssh_devices = config.get('ssh_devices', [])
            if not ssh_devices:
                logger.warning('没有配置SSH设备，跳过基线检查')
            else:
                # 执行基线检查
                results = check_devices_baseline(ssh_devices)
                logger.info('基线检查完成')
                
                # 打印结果统计
                success_count = sum(1 for result in results.values() if not result.get('failed', False))
                failed_count = len(results) - success_count
                logger.info(f'基线检查结果: 成功 {success_count} 台, 失败 {failed_count} 台')
        except Exception as e:
            logger.error(f'基线检查失败: {str(e)}')
    elif action == 'summary':
        # 生成汇总报告
        logger.info("开始生成汇总报告...")
        try:
            from src.modules.baseline.generate_summary_report import generate_summary_report
            summary_report_path = generate_summary_report()
            if summary_report_path:
                logger.info(f"汇总报告生成成功: {summary_report_path}")
            else:
                logger.error("汇总报告生成失败")
        except Exception as e:
            logger.error(f"汇总报告生成失败: {str(e)}")
        logger.info("汇总报告生成完成")
    elif action == 'process' and order_path:
        logger.info(f'开始处理订单 {order_path}')
        try:
            # 获取模板目录
            template_dir = os.path.join(base_dir, 'templates')
            # 使用OrderProcessor类处理订单
            OrderProcessor(order_path, config, template_dir) 
            # logger.info(f'订单处理完成，生成内容 {content}')
        except Exception as e:
            logger.error(f'订单处理失败: {str(e)}')
    elif action == 'generate':
        logger.info('开始生成配置')
        try:
            # 这里将实现配置生成逻辑
            logger.info('配置生成完成')
        except Exception as e:
            logger.error(f'配置生成失败: {str(e)}')
    else:
        logger.error('请提供有效的动作和参数')
        parser.print_help()


if __name__ == '__main__':
    # 在Python代码中直接调用
    main()