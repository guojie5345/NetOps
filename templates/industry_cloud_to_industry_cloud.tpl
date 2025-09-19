1. 登录T38A3(6U)-FC-FWhw12004A（172.16.190.35），{{ action }}相关策略：
1) 安全策略设置-{{ action }} (策略 -> 安全策略 -> 安全策略)
名称：VPC互访015
源安全区域：any，源地址：{{ eip_ips }}，
目的安全区域: any，目的地址：{{requirement.目的IP}}，
服务：保持当前端口状态
动作：{{ action }}

2. 登录T38A5A6(21U)-FC-DSu7800A（172.16.190.37），{{ action }}相关配置：
ip route-static vpn_instance VPC-trust {{requirement.目的IP}} {{requirement.目的子网掩码}} {{ vpn_instance_B }} {{requirement.目的网关-1}} description To_FC_{{ customer.origination }}-VPC
ip route-static vpn-instance VPC-trust {{requirement.目的IP}} {{requirement.目的子网掩码}} {{ vpn-instance-B }} {{requirement.目的网关-2}} description To_FC_{{ customer.origination }}-VPC
ip route-static vpn-instance {{ vpn-instance-B }} {{requirement.源IP}} {{requirement.目的子网掩码}} {{requirement.目的网关-1}} description To_FC_{{ customer.origination }}-VPC

ip route-static vpn-instance VPC-trust {{requirement.目的IP}} {{requirement.目的子网掩码}} {{ vpn-instance-B }} {{requirement.目的网关-1}} description To_FC_{{ customer.origination }}-VPC
ip route-static vpn-instance VPC-trust {{requirement.目的IP}} {{requirement.目的子网掩码}} {{ vpn-instance-B }} {{requirement.目的网关-2}} description To_FC_{{ customer.origination }}-VPC
ip route-static vpn-instance {{ vpn-instance-B }} {{requirement.源IP}} {{requirement.目的子网掩码}} {{requirement.目的网关-1}} description To_FC_{{ customer.origination }}-VPC
