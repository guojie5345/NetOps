1. 登录T38A3(6U)-FC-FWhw12004A（172.16.190.35），{{ operation }}相关策略：
1) 安全策略设置-{{ operation }} (策略 -> 安全策略 -> 安全策略)
名称：VPC互访015
源安全区域：any，源地址：{{ requirement.源IP }}，
目的安全区域: any，目的地址：{{ requirement.目的IP }}，
服务：{{ requirement.目的端口 }}
动作：{{ operation }}

2. 登录T38A5A6(21U)-FC-DSu7800A（172.16.190.37），{{ operation }}相关配置：
{%- for combin_net_info in combin_net_infos %}
vlan {{ combin_net_info.vlan }}
 name {{combin_net_info.description }}

ip vpn-instance {{ combin_net_info.vpn_instance }}
 description {{combin_net_info.description }}

interface Vlan-interface{{ combin_net_info.vlan }}
 description {{combin_net_info.description }}
 ip binding vpn-instance {{ combin_net_info.vpn_instance }}
 ip address {{ combin_net_info.ip_a }} 255.255.255.248

ip route-static vpn_instance VPC-trust {{combin_net_info.cidr|replace('/',' ')}} vpn-instance {{ combin_net_info.vpn_instance }} {{combin_net_info.ip_b }} description {{combin_net_info.description }}
ip route-static vpn-instance VPC-trust {{combin_net_info.cidr|replace('/',' ')}} vpn-instance {{ combin_net_info.vpn_instance }} {{combin_net_info.ip_c }} description {{combin_net_info.description }}
ip route-static vpn-instance {{ combin_net_info.vpn_instance }} 172.28.0.0 16 vpn-instance VPC-trust 172.27.255.33 description To_FC_Other_VPC
{% endfor %}

