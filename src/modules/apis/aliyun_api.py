import os
import json
from itertools import product

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from aliyunsdkcore.auth.credentials import AccessKeyCredential
from aliyunsdkecs.request.v20140526 import DescribeInstancesRequest


class AliYunApiClient:
    def __init__(self, region_id='cn-zhengzhou-zcefc-d01', access_key_id='FpiqDG63LhQezSRa',
                 access_key_secret='menGywFUNsMoN7lTUfMhvKvWGiHHhA', timeout=10000):
        """
        初始化阿里云ECS客户端

        :param region_id: 地域ID（如 cn-zhengzhou-zcefc-d01）
        :param access_key_id: 访问密钥ID
        :param access_key_secret: 访问密钥Secret
        :param timeout: 请求超时时间（单位：ms）
        """
        # 初始化凭证和客户端
        self.credentials = AccessKeyCredential(access_key_id, access_key_secret)
        self.client = AcsClient(
            region_id=region_id,
            credential=self.credentials,
            timeout=timeout
        )

        # 固定请求参数（可根据需求改为可配置）

        self.action_name = None
        # self.domain = "ecs-internal.res.cloud.zce.cn"
        self.protocol = "http"
        self.method = "POST"
        self.content_type = "application/json"

    def _api_request(self, product, domain, version, action_name, page_size, filter_params=None, ):
        """
        通用API请求方法（私有）

        :param action_name: API操作名称
        :param page_size: 每页显示数量
        :param filter_params: 过滤参数键值对（如 {"PrimaryIpAddress": "172.28.134.122", "NetworkInterfaceId": "eni-xxx"}）
        :return: API响应结果（字节流）
        """
        request = CommonRequest()
        # 设置产品接口信息（公共部分，保持不变）
        request.set_product(product)
        request.set_action_name(action_name)
        request.set_domain(domain)
        request.set_version(version)
        request.set_method(self.method)
        request.set_protocol_type(self.protocol)
        # 设置必选Header（保持不变）
        request.add_header("x-acs-caller-sdk-source", "pycharm")
        # 分页参数改为直接使用入参
        request.add_query_param("PageSize", str(page_size))
        # 处理多组过滤参数（支持字典内多个键值对）
        if filter_params:
            for key, value in filter_params.items():
                if value is not None:  # 跳过值为None的参数（避免传递无效参数）
                    request.add_query_param(key, value)
        # 设置内容类型（保持不变）
        request.set_content_type(self.content_type)
        return self.client.do_action_with_exception(request)

    def describe_network_interfaces(self, page_size=1000, primary_ip=None, network_interface_id=None, **extra_filters):
        """
        查询网络接口信息（支持多过滤条件）

        :param page_size: 每页显示数量
        :param primary_ip: 主IP地址过滤（可选）
        :param network_interface_id: 网络接口ID过滤（可选）
        :param extra_filters: 扩展过滤参数（键为API参数名，值为参数值，如 {"VpcId": "vpc-xxx"}）
        """
        # 合并显式参数和扩展参数
        filter_params = {
            "PrimaryIpAddress": primary_ip,
            "NetworkInterfaceId": network_interface_id,
            **extra_filters  # 允许通过**kwargs传递更多过滤条件
        }
        # 过滤掉值为None的键（避免传递无效参数）
        filter_params = {k: v for k, v in filter_params.items() if v is not None}
        return self._api_request(
            product="ecs",
            domain='ecs-internal.res.cloud.zce.cn',
            version="2014-05-26",
            action_name="describeNetworkInterfaces",
            page_size=page_size,
            filter_params=filter_params or None  # 无过滤条件时传None
        )

    def describe_instances(self, page_size=1000, private_ip_addresses=None, instance_ids=None, **extra_filters):
        """
        查询ECS实例信息（支持多过滤条件）

        :param page_size: 每页显示数量
        :param private_ip_addresses: 私有IP地址过滤（可选）
        :param instance_ids: 实例ID列表过滤（可选）
        :param extra_filters: 扩展过滤参数（键为API参数名，值为参数值，如 {"VpcId": "vpc-xxx"}）
        """
        filter_params = {
            "PrivateIpAddress": private_ip_addresses,
            "InstanceIds": instance_ids,
            **extra_filters
        }
        filter_params = {k: v for k, v in filter_params.items() if v is not None}

        return self._api_request(
            product="ecs",
            domain='ecs-internal.res.cloud.zce.cn',
            version="2014-05-26",
            action_name="describeInstances",
            page_size=page_size,
            filter_params=filter_params or None
        )

    def describe_eip_addresses(self, page_size=100, eip_addresses=None, status=None, **extra_filters):
        """
        查询EIP信息（支持多过滤条件）

        :param page_size: 每页显示数量
        :param eip_addresses: EIP地址过滤（可选）
        :param status: 状态（可选）
        :param extra_filters: 扩展过滤参数（键为API参数名，值为参数值，如 {"VpcId": "vpc-xxx"}）
        """
        filter_params = {
            "EipAddress": eip_addresses,
            "Status": status,  # Associating 绑定中 Unassociating：解绑中 InUse：已分配 Available：可用
            **extra_filters
        }
        filter_params = {k: v for k, v in filter_params.items() if v is not None}

        return self._api_request(
            product='Vpc',
            domain='vpc-internal.res.cloud.zce.cn',
            version='2016-04-28',
            action_name="DescribeEipAddresses",
            page_size=page_size,
            filter_params=filter_params or None
        )


if __name__ == "__main__":
    # 使用示例，可根据实际情况修改参数
    client = AliYunApiClient(
        # region_id='cn-zhengzhou-zcefc-d01',
        # access_key_id='FpiqDG63LhQezSRa',
        # access_key_secret='menGywFUNsMoN7lTUfMhvKvWGiHHhA'
    )

    # 查询网络接口（可传入自定义参数）
    # resp = client.describe_network_interfaces(
    #     page_size=1000,
    #     primary_ip="172.28.134.122"
    # )

    # 查询ECS实例接口（可传入自定义参数）
    # resp = client.describe_instances(
    #     page_size=1000,
    # )

    #
    # 查询EIP（可传入自定义参数）
    resp = client.describe_eip_addresses(
        page_size=100
    )

    print(str(resp, encoding='utf-8'))
