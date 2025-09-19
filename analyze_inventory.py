#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import yaml
import json
import pandas as pd

def analyze_yaml_files():
    """分析生成的YAML文件"""
    
    # 读取Excel文件
    try:
        df = pd.read_excel('e:/Development/Python/NetOps/data/input/zabbix_host_configs.xlsx')
        print(f"Excel文件中的设备总数: {len(df)}")
    except Exception as e:
        print(f"读取Excel文件时出错: {e}")
        return
    
    # 分析完整的hosts.yaml
    try:
        with open('e:/Development/Python/NetOps/data/output/inventory/hosts.yaml', 'r', encoding='utf-8') as f:
            all_hosts = yaml.safe_load(f)
        print(f"hosts.yaml中的设备数量: {len(all_hosts)}")
        
        # 统计平台类型分布
        platform_count = {}
        for host, data in all_hosts.items():
            platform = data.get('platform', 'unknown')
            platform_count[platform] = platform_count.get(platform, 0) + 1
        
        print("\n所有设备平台类型分布:")
        for platform, count in sorted(platform_count.items()):
            print(f"  {platform}: {count}")
    except Exception as e:
        print(f"读取hosts.yaml时出错: {e}")
    
    # 分析network_hosts.yaml
    try:
        with open('e:/Development/Python/NetOps/data/output/inventory/network_hosts.yaml', 'r', encoding='utf-8') as f:
            network_hosts = yaml.safe_load(f)
        print(f"\nnetwork_hosts.yaml中的设备数量: {len(network_hosts)}")
        
        # 统计平台类型分布
        platform_count = {}
        for host, data in network_hosts.items():
            platform = data.get('platform', 'unknown')
            platform_count[platform] = platform_count.get(platform, 0) + 1
        
        print("\n网络设备平台类型分布:")
        for platform, count in sorted(platform_count.items()):
            print(f"  {platform}: {count}")
            
        # 显示前10个网络设备
        print("\n前10个网络设备:")
        count = 0
        for host, data in network_hosts.items():
            print(f"  {host}: {data}")
            count += 1
            if count >= 10:
                break
    except Exception as e:
        print(f"读取network_hosts.yaml时出错: {e}")
    
    # 分析network_groups.yaml
    try:
        with open('e:/Development/Python/NetOps/data/output/inventory/network_groups.yaml', 'r', encoding='utf-8') as f:
            network_groups = yaml.safe_load(f)
        print(f"\nnetwork_groups.yaml中的组数量: {len(network_groups)}")
        
        print("\n网络设备组列表:")
        for group_name in sorted(network_groups.keys()):
            print(f"  {group_name}")
    except Exception as e:
        print(f"读取network_groups.yaml时出错: {e}")

if __name__ == "__main__":
    analyze_yaml_files()