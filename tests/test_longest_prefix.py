# -*- coding: utf-8 -*-
import ipaddress

# 模拟network_group_mapping配置
network_group_mapping = {
    "131.6.200.0/24": "core_network_devices",
    "172.16.190.0/28": "mgt_group",
    "172.16.190.0/24": "ali_group",
    "172.16.191.0/24": "distribution_layer_am11",
    "172.16.192.0/24": "core_layer_am11",
    "172.16.193.0/24": "management_am11",
    "172.16.201.0/24": "server_network",
    "172.16.233.0/24": "compute_cluster",
    "172.16.235.0/24": "storage_network",
    "172.16.244.0/24": "office_network",
    "172.16.245.0/24": "development_network",
    "172.16.247.0/24": "testing_network",
    "172.16.248.0/24": "management_servers",
    "172.16.253.0/24": "terminal_servers",
    "127.0.0.0/24": "loopback_addresses"
}

# 按照网络前缀长度排序，最长前缀优先
sorted_networks = sorted(
    network_group_mapping.items(), 
    key=lambda x: ipaddress.ip_network(x[0], strict=False).prefixlen, 
    reverse=True
)

print("排序后的网络列表（最长前缀优先）:")
for network, group in sorted_networks:
    print(f"  {network} ({ipaddress.ip_network(network, strict=False).prefixlen} bits) -> {group}")

# 测试特定IP地址
test_ip = "172.16.190.1"
print(f"\n测试IP地址: {test_ip}")

# 检查IP是否在指定网段内
def ip_in_network(ip, network):
    try:
        ip_obj = ipaddress.ip_address(ip)
        net_obj = ipaddress.ip_network(network, strict=False)
        return ip_obj in net_obj
    except ValueError:
        return False

# 查找匹配的网段
matched_network = None
matched_group = None
for network, group_name in sorted_networks:
    if ip_in_network(test_ip, network):
        matched_network = network
        matched_group = group_name
        break

if matched_network:
    print(f"匹配的网段: {matched_network} -> {matched_group}")
else:
    print("未找到匹配的网段")