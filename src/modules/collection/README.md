# 信息采集模块

## 概述

信息采集模块提供基于API和SSH的信息采集功能，用于从网络设备和云平台收集信息。

## 功能特性

1. **SSH信息采集**
   - 支持多种网络设备（Cisco, Huawei, HP Comware等）
   - 采集设备基本信息、接口信息、ARP表等
   - 自动处理连接和认证

2. **API信息采集**
   - 支持RESTful API接口
   - 采集云平台资源信息（服务器、网络、存储等）
   - 自动处理认证和重试

3. **统一接口**
   - 整合SSH和API采集功能
   - 支持批量采集
   - 数据保存和导出

## 使用方法

### 1. 配置采集器

创建配置文件 `config.json`:

```json
{
  "ssh_devices": [
    {
      "device_type": "cisco_ios",
      "host": "172.16.1.1",
      "username": "admin",
      "password": "password",
      "port": 22
    }
  ],
  "api_endpoints": [
    {
      "url": "https://api.example.com/v1",
      "api_key": "your_api_key_here",
      "resource_types": ["servers", "networks", "volumes"]
    }
  ]
}
```

### 2. 使用采集器

```python
from src.modules.collection.collector import collect_all

# 加载配置
with open('config.json', 'r') as f:
    config = json.load(f)

# 采集所有信息
data = collect_all(config, 'output.json')

# 或者不保存到文件
data = collect_all(config)
```

### 3. 单独使用SSH采集器

```python
from src.modules.collection.ssh_collector import SSHCollector

device_info = {
    "device_type": "cisco_ios",
    "host": "172.16.1.1",
    "username": "admin",
    "password": "password",
    "port": 22
}

collector = SSHCollector(device_info)
if collector.connect():
    # 采集基本信息
    basic_info = collector.collect_basic_info()
    
    # 采集接口信息
    interface_info = collector.collect_interface_info()
    
    # 断开连接
    collector.disconnect()
```

### 4. 单独使用API采集器

```python
from src.modules.collection.api_collector import APICollector

collector = APICollector("https://api.example.com/v1", "your_api_key_here")

# 采集服务器信息
servers = collector.collect_server_info()

# 采集特定服务器信息
server = collector.collect_server_info("server_id")
```

## 依赖

- netmiko: 用于SSH连接
- requests: 用于API请求

## 支持的设备类型

### SSH设备
- Cisco IOS (`cisco_ios`)
- Huawei (`huawei`)
- HP Comware (`hp_comware`)
- 更多设备类型请参考netmiko文档

### API资源类型
- Servers/Instances
- Networks
- Volumes/Storage
- 自定义资源类型

## 注意事项

1. 确保网络连接正常
2. 确保用户名和密码正确
3. 对于API采集，确保API密钥有效
4. 采集大量设备时，注意性能影响