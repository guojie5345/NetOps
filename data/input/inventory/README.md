# Inventory YAML 文件使用说明

## 文件结构

本目录包含以下文件：
- `hosts.yaml`: 输入的主机配置文件
- `device_mapping_config.yaml`: 设备类型映射配置文件
- `README.md`: 本说明文件

## 生成的输出文件

通过运行 `scripts/generate_inventory_from_yaml.py` 脚本，会生成以下输出文件：
- `hosts_{timestamp}.yaml`: 主机配置文件
- `groups_{timestamp}.yaml`: 组配置文件
- `default_{timestamp}.yaml`: 默认配置文件
- `config_{timestamp}.yaml`: 主配置文件

## 使用方法

1. 确保输入的 `hosts.yaml` 文件格式正确
2. 根据需要修改 `device_mapping_config.yaml` 中的设备类型映射规则
3. 运行脚本生成输出文件：
   ```bash
   python scripts/generate_inventory_from_yaml.py
   ```
4. 生成的文件将保存在 `data/output/inventory/` 目录中

## 配置说明

### device_mapping_config.yaml

该文件定义了如何根据主机名匹配设备类型和组：

```yaml
device_mapping:
  - pattern: "cisco"      # 匹配模式（正则表达式）
    group: "dev_group"    # 对应的组
    platform: "cisco_ios" # 对应的平台
```

### 输出文件格式

生成的YAML文件与Excel转换工具生成的文件格式一致，可直接用于Netmiko等网络自动化工具。

## 设备类型映射规则

- **Cisco设备**: 包含 "cisco"、"3750"、"3850"、"2960"、"4500"、"4948" 等关键词
- **Cisco NX-OS设备**: 包含 "n3548"、"nxos" 等关键词
- **华为设备**: 包含 "huawei"、"eudemon"、"s5700"、"s6700"、"s7700"、"s9300"、"hw5720"、"hw8861" 等关键词
- **Juniper设备**: 包含 "junip"、"j5100"、"j1000"、"j2000" 等关键词
- **HP设备**: 包含 "hp"、"procurve"、"comware"、"5560"、"5130"、"6520"、"3610"、"5030"、"u5200"、"u7800"、"7800"、"6600"、"hs5560"、"hs5130"、"hs6520"、"hs5110"、"hs5200" 等关键词
- **H3C设备**: 包含 "h3c" 等关键词
- **默认设备**: 所有其他设备默认为 "generic_termserver"

## 注意事项

1. 如果输入文件中的主机已经指定了platform，则优先使用指定的platform
2. 设备类型映射是按照配置文件中的顺序进行匹配的，第一个匹配的规则将被应用
3. 可以根据实际需求修改 `device_mapping_config.yaml` 文件中的映射规则