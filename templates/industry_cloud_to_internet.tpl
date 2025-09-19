1. 登录T38a7(41U)-ISP-LBsx1000A（172.16.190.21），{{ operation }}相关策略：
{%- if ad_eip_address_exist==False %}
创建地址表条目(或加入已存在的地址表)
名称： {{ ad_eip_address_name}}；地址：{{ eip_ips }}
{%- elif ad_isp_address_exist==False %}
名称： {{isp_ips[0]}}和{{isp_ips[1]}}-{{ customer.organization }}；地址：{{ isp_ips }}
{%- endif %}

源地址转换-{{ operation }}
{%- if customer.organization=="信达期货" %}
******** 请注意名称后的序号，并人工确认“名称”并修改名称。 ********
{% endif %}
位置序号: （预留）， 名称：{{ customer.organization }}-源转换-电信IPV4，
源地址 入接口：指定链路，inside-net9， 源IP地址：用户地址集，详细地址：{{ ad_eip_address_name }}
目的地址 出接口：指定链路，vlan1897-CT-IPV4(公用)， 目的IP地址：所有IP
协议条件 协议类型：All
转换规则 转换源IP：指定IP：{{ requirement.公网IP[0] }}， 转换策略：源IP和目的IP哈希， 源端口策略：保持

位置序号: （预留）， 名称：{{ customer.organization }}-源转换-移动IPV4，
源地址 入接口：指定链路，inside-net9， 源IP地址：用户地址集，详细地址：{{ ad_eip_address_name }}
目的地址 出接口：指定链路，vlan1898-CM-IPV4(公用)， 目的IP地址：所有IP
协议条件 协议类型：All
转换规则 转换源IP：指定IP：{{ requirement.公网IP[1] }}， 转换策略：源IP和目的IP哈希， 源端口策略：保持

智能路由-{{ operation }}
{% if customer.organization=="信达期货" %}
******** 请注意名称后的序号，并人工确认“名称”并修改名称。 ********
{% endif -%}
名称：{{ customer.organization }}路由
源IP：用户地址集 EIP-{{ customer.organization }}
目的类型：所有IP
入口链路：所有链路
协议条件：所有协议
出口链路： vlan1898-CM-IPV4（公用） vlan1897-CT-IPV4（公用）
链路选择策略：加权最小流量
生效时间：全天

2.登录T38A5(26U)-ISP-FWss6600A（172.16.190.23），{{ operation }}相关策略：
1) iQoS设置-{{ operation }} (策略 -> iQoS -> 策略)
新建对象->地址薄：IQOS{{ customer.organization }}EIP
地址：{{ eip_ips }}

修改策略名称：{{ customer.organization }}访问互联网
新增源地址：{{ eip_ips }}

新增IQoS策略：{{ customer.organization }}互联网-5M
匹配条件：
条目1： 源地址条目：IQOS{{ customer.organization }}EIP
条目2： 目的地址条目：IQOS{{ customer.organization }}EIP
流控动作：
正向： 最小1Mbps 最大5Mbps
反向： 最小1Mbps 最大5Mbps
限制类型：不限制
2) 安全策略设置-{{ operation }} (安全策略 -> 策略)
名称：{{ customer.organization }}-{{ customer.system_name }}上网
源安全域：trust，源地址：{{ eip_ips }}，
目的安全域: untrust，目的地址：{{requirement.目的IP}}，
服务：{{ requirement.目的端口 }}
动作：{{ operation }}
*********** 策略附加项检查 ***********
防护状态  病毒过滤: predef_high， 入侵防御：predef_default， URL过滤：no-url， 沙箱防护：predef_high
数据安全  上网行为审计:no-nbr
选项   时间表：{{ requirement.生效时间 }}， 记录日志:勾选“策略拒绝”、“会话开始”、“回话结束”
