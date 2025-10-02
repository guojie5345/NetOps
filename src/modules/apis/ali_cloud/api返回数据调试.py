#!/usr/bin/env python
# -*- coding: utf-8 -*-
# _*_ coding:utf-8 _*_
# @Project  :DevOps
# @FileName :api返回数据调试.py
# @Time     :2025/7/14 14:55
# @Author   :George

import jsonpath
import json
import pprint


def extract_jsonpath(data, path, default=None):
    """
    使用 jsonpath 从数据中提取值，如果未匹配到则返回默认值。

    Args:
        data (dict): 要提取数据的 JSON 对象。
        path (str): jsonpath 表达式。
        default: 未匹配到值时返回的默认值，默认为 None。

    Returns:
        匹配到的值或默认值。
    """
    result = jsonpath.jsonpath(data, path)
    return result[0] if result else default


with open("instances.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# 初始化字典存储 {InstanceId: [PrimaryIpAddress列表]}
instance_ip_map = {}

# 遍历每个实例对象（保持原数据遍历方式）
for instance in data["Instances"]["Instance"]:
    # 使用jsonpath提取当前实例的InstanceId和instance_name
    instance_id = extract_jsonpath(instance, "$.InstanceId")
    instance_name = extract_jsonpath(instance, "$.InstanceName")
    if not instance_id or not instance_name:
        print(f"实例缺少 InstanceId 或 InstanceName，跳过处理")
        continue
    instance_id_name = f"{instance_id}({instance_name})"

    # 使用 jsonpath 提取当前实例下 DepartmentName 和 ResourceGroupName
    department_name = extract_jsonpath(instance, "$.DepartmentName")
    resource_group_name = extract_jsonpath(instance, "$.ResourceGroupName")
    description = f"ECS_{department_name}_{resource_group_name}" if department_name and resource_group_name else "ECS_未知_未知"

    # 使用 jsonpath 提取当前实例下所有 PrimaryIpAddress
    ip_list = extract_jsonpath(instance, "$.NetworkInterfaces.NetworkInterface[*].PrimaryIpAddress", [])

    # 使用 jsonpath 提取当前实例下所有 EipAddress
    eip_address = extract_jsonpath(instance, "$.EipAddress.IpAddress")
    if not eip_address:
        print(f"实例 {instance_id_name}，未找到有效的 EipAddress！ ")

    # 关联实例ID与IP列表（跳过无效ID）
    if instance_id_name:
        instance_data = {"description": description, "ips": ip_list}
        if eip_address:
            instance_data["eip"] = eip_address
        instance_ip_map[instance_id_name] = instance_data

# 打印结果
pprint.pprint(instance_ip_map)
# print("实例ID与IP地址映射（jsonpath实现）：", instance_ip_map)
