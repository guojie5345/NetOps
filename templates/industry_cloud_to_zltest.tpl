1.登录T38A5(26U)-CDL-FWss6600A（172.16.190.41），进入虚拟子墙(ZLTEST-vFW)，{{ action }}相关策略：
1) 安全策略设置-{{ action }} (策略 -> 安全策略 -> 策略)
ID：3
名称：FC-用户访问ZLTest网
源安全域：trust，新增源地址：{{ eip_ips }}，
目的安全域: untrust，目的地址：{{requirement.目的IP}}，
服务：保持当前端口状态
动作：{{ action }}

