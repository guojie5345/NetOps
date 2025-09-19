#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""ITSM变更自动化工具主程序"""

import sys
import os

# 获取当前文件所在目录的绝对路径
base_dir = os.path.dirname(os.path.abspath(__file__))
# 添加项目根目录到系统路径
sys.path.insert(0, base_dir)

import logging
import argparse
import json
from src.modules.processing.process_order import process_order
from src.modules.ali_cloud.aliyun_api import AliYunApiClient
from src.core.config_manager import ConfigManager
from src.utils.logger import setup_logger


# 注意：需要导入DescribeInstancesRequest
# 这里假设它来自aliyun.ecs.request.v20140526 import DescribeInstancesRequest
# 请根据实际情况调整导入路径
try:
    from aliyun.ecs.request.v20140526 import DescribeInstancesRequest
except ImportError:
    # 如果导入失败，创建一个模拟类以避免运行时错误
    class DescribeInstancesRequest:
        pass
    logging.warning('DescribeInstancesRequest导入失败，使用模拟类替代')



def get_aliyun_resource_info(aliyun_config):
    """获取阿里云资源信息"""
    aliyun_client = AliYunApiClient(
        region_id=aliyun_config['region_id'],
        access_key_id=aliyun_config['access_key_id'],
        access_key_secret=aliyun_config['access_key_secret']
    )
    # 调用DescribeInstancesRequest获取实例列表
    try:
        request = DescribeInstancesRequest()
        # 设置请求参数
        request.set_accept_format('json')
        # 调用API获取实例列表
        # response = aliyun_client.client.do_action_with_exception(request)
        # return json.loads(response)
        return []  # 临时返回空列表，避免运行错误
    except Exception as e:
        logging.error(f'获取阿里云资源信息失败: {str(e)}')
        return []


# 修改main函数，支持直接调用
def main(config_path=None, order_path=None, action=None):
    """
    主程序入口

    Args:
        config_path (str, optional): 配置文件路径. Defaults to None.
        order_path (str, optional): 订单文件路径. Defaults to None.
        action (str, optional): 执行动作: process(处理订单), collect(采集数据), generate(生成配置). Defaults to None.
    """
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='ITSM变更自动化工具')
    parser.add_argument('--config', type=str, default='src/config/config.json', help='配置文件路径')
    parser.add_argument('--order', type=str, help='订单文件路径')
    parser.add_argument('--action', type=str, choices=['process', 'collect', 'generate'], default='process',
                        help='执行动作: process(处理订单), collect(采集数据), generate(生成配置)')

    # 如果没有提供参数，则使用命令行参数
    if config_path is None and order_path is None and action is None:
        args = parser.parse_args()
        config_path = args.config
        order_path = args.order
        action = args.action
    # 如果提供了部分参数，则使用提供的参数，其余使用默认值
    elif config_path is None:
        args = parser.parse_args([])
        config_path = args.config
    elif action is None:
        action = 'process'

    # 初始化日志
    setup_logger()
    logger = logging.getLogger(__name__)
    logger.info('ITSM变更自动化工具启动')

    # 加载配置
    config_manager = ConfigManager(config_path)
    config = config_manager.load_config()
    logger.info('配置加载完成')

    # 根据动作执行不同的功能
    if action == 'process' and order_path:
        logger.info(f'开始处理订单: {order_path}')
        try:
            content = process_order(order_path)
            logger.info(f'订单处理完成，生成内容: {content}')
        except Exception as e:
            logger.error(f'订单处理失败: {str(e)}')
   # elif action == 'collect':
   #     logger.info('开始采集数据')
   #     try:
   #         # 示例: 采集阿里云资源信息
   #         aliyun_info = get_aliyun_resource_info(config['aliyun'])
   #         logger.info(f'数据采集完成，共采集 {len(aliyun_info)} 条记录')
   #     except Exception as e:
   #         logger.error(f'数据采集失败: {str(e)}')
   # elif action == 'generate':
   #     logger.info('开始生成配置')
   #     try:
   #         # 这里将实现配置生成逻辑
   #         logger.info('配置生成完成')
   #     except Exception as e:
   #         logger.error(f'配置生成失败: {str(e)}')
   # else:
   #     logger.error('请提供有效的动作和参数')
   #     parser.print_help()


if __name__ == '__main__':
    # 在Python代码中直接调用
    main(config_path='src/config/config.json',
         order_path='data/input/order/【网络资源】网络资源服务申请单-浙商期货-白名单.xlsx',
         action='process')