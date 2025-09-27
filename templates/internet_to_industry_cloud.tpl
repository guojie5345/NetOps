1. 登录T38a7(41U)-ISP-LBsx1000A（172.16.190.21），{{ operation }}相关策略：
1） 目的地址转换 
位置序号：（预留）， 
名称： {{ customer.organization }}-{{ customer.system_name }};
源地址入接口： 指定链路，vlan1897-CT-IPV4(公用)，vlan1898-CM-IPV4(公用);
源IP地址： 所有IP;
目的IP地址： 用户地址集 -> {{ ad_isp_address_name }} -> {{ isp_ips }};
协议条件 协议类型：TCP; 源端口范围：{{ requirement.源端口 }};  目的端口范围：{{ requirement.公网端口 }};
转换规则 转换目的IP： 指定IP -> 详细地址：{{ eip_ips }};  转换端口：{{ requirement.目的端口 }};

2. 登录T38A5(26U)-ISP-FWss6600A（172.16.190.23），{{ operation }}相关策略：
名称：{{ customer.organization }}-{{ customer.system_name }}
源安全域：untrust，源地址：{{ requirement.源主机 }}，
目的安全域: trust，目的地址：{{ eip_ips }}，服务：{{ requirement.目的端口 }} 
动作：{{ operation }}
*********** 策略附加项检查 ***********
防护状态  病毒过滤: predef_high， 入侵防御：predef_default， URL过滤：no-url， 沙箱防护：predef_high
数据安全  上网行为审计:no-nbr
选项   时间表：{{ requirement.生效时间 }}， 记录日志:勾选“策略拒绝”、“会话开始”、“回话结束”
