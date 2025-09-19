import yaml

# 查看network_hosts.yaml中前几个设备的详细信息
with open('e:/Development/Python/NetOps/data/output/inventory/network_hosts.yaml', 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)
    
print('前10个网络设备:')
count = 0
for k, v in data.items():
    print(f'{k}: {v}')
    count += 1
    if count >= 10:
        break

print('\n' + '='*50 + '\n')

# 查看Excel中前几行数据
import pandas as pd
df = pd.read_excel('e:/Development/Python/NetOps/data/input/zabbix_host_configs.xlsx')
print('Excel文件前10行数据:')
print(df.head(10))