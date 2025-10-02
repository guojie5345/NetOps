#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# @Project  :NetOps
# @FileName :phpipam_api.py
# @Time     :2025/9/5 14:12
# @Author   :George


class PhpIpamApiClient:
    """
    phpIPAM API客户端类，用于与phpIPAM系统交互，获取IP地址和子网信息。

    phpIPAM是一个开源的IP地址管理系统，该类封装了连接phpIPAM API的基础操作，
    提供获取地址和子网数据的方法。
    """

    def __init__(self):
        """
        初始化PhpIpamApiClient实例，配置连接参数并建立API连接。

        连接参数包括phpIPAM的URL、应用ID、认证凭据以及SSL验证设置，
        并通过phpypam库创建API客户端实例。
        """
        self.conn_params = dict(
            url="https://172.16.248.5",
            app_id='update_ip',
            username='guojie',
            password='1qazXSW@#EDC',
            ssl_verify=False
        )
        self.ipam_api = phpypam.api(**self.conn_params)

    def get_addresses(self):
        """
        获取phpIPAM中所有IP地址记录。

        通过调用phpIPAM API的addresses控制器，获取系统中所有已配置的IP地址信息。

        :return: 包含所有IP地址记录的列表，每条记录为字典格式
        """
        return self.ipam_api.get_entity(controller='addresses', controller_path='all')

    def get_subnets(self):
        """
        获取phpIPAM中所有子网记录。

        通过调用phpIPAM API的subnet控制器，获取系统中所有已配置的子网信息。

        :return: 包含所有子网记录的列表，每条记录为字典格式
        """
        return self.ipam_api.get_entity(controller='subnets', controller_path='all')
