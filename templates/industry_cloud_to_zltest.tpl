1.登录T38A5(26U)-CDL-FWss6600A（172.16.190.41），进入虚拟子墙(ZLTEST-vFW），{{ operation }}相关策略：
1) 安全策略设置-{{ operation }} (策略 -> 安全策略 -> 策略)
名称：{{ customer.organization }}-证联网测试网
源安全域：ZLTest-vFW-trust，源地址：{% for net in nets %}{{ net.cidr }}{% if not loop.last %},{% endif %}{% endfor %}，
目的安全域: ZLTest-vFW-untrust，目的地址：{{ requirement.目的IP }}，
服务：{{ requirement.目的端口}}
动作：{{ operation }}