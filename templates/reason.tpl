接{{ customer['organization'] }}变更需求，计划{{ requirement['操作'] }}{{ customer['system_name'] }}{{ source_target_pair[0] }}访问{{ source_target_pair[1] }}的策略。
源归属: {{ requirement['源归属'] }}， 源主机: {{ requirement['源主机'] }}，
目的归属: {{ requirement['目的归属'] }}， 目的主机: {{ requirement['目的主机'] }}，
源IP: {{ requirement['源IP'] }}，源端口: {{ requirement['源端口'] }}
目的IP: {{ requirement['目的IP'] }}，目的端口: {{ requirement['目的端口'] }}
{%- if requirement['源归属'] == '互联网' or requirement['目的归属'] == '互联网' %}
公网IP: {{ requirement['公网IP'] }}，公网端口: {{ requirement['公网端口'] }}
{% endif -%}
协议: {{ requirement['协议'] }}，生效时间:{{ requirement['生效时间'] }}
