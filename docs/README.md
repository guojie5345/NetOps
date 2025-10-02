# ITSM变更自动化工具

## 项目概述

ITSM变更自动化工具是一个用于自动化IT服务管理(ITSM)中变更流程的Python项目。它能够自动部署应用程序到目标服务器，采集设备信息，处理采集的数据，生成配置文件，并管理应用程序的配置。

## 功能特点

1. **自动部署** - 自动部署应用程序到目标服务器
2. **信息采集** - 利用设备API或SSH方式采集设备信息
3. **信息处理** - 将采集后的信息转换为可用于后续处理的格式
4. **配置生成** - 通过配置模板，将处理后的信息运用到配置模板中，生成最终的配置文件
5. **配置管理** - 利用配置文件管理应用程序的配置信息
6. **自动备份** - 自动备份数据库和文件
7. **自动监控** - 自动监控服务器和应用程序的运行状态
8. **自动报警** - 自动报警当服务器或应用程序出现问题时
9. **基线检查** - 检查设备配置是否符合安全基线要求
10. **Excel转Inventory** - 从Excel文件生成设备Inventory文件

## 技术栈

- Python 3.12
- requests - 用于发送HTTP请求和API调用
- pytest - 用于编写和运行测试用例
- netmiko - 用于SSH连接和配置设备
- jinja2 - 用于模板渲染
- selenium - 用于浏览器自动化测试
- openpyxl - 用于读写Excel文件
- pandas - 用于数据处理和分析
- mysql-connector-python - 用于连接和操作MySQL数据库
- sendgrid - 用于发送邮件

## 目录结构

```
NetOps/
├── config/                 # 配置文件目录
│   ├── device/            # 设备相关配置
│   ├── itsm/              # ITSM相关配置
│   └── rule/              # 规则配置文件
├── data/                  # 数据目录
│   ├── input/             # 输入数据
│   │   └── inventory/     # Inventory文件
│   └── output/            # 输出数据
│       └── debug_test/    # 调试测试输出
├── docs/                  # 文档目录
├── logs/                  # 日志目录
├── src/                   # 源代码目录
│   └── modules/           # 功能模块
│       ├── apis/          # API相关模块
│       ├── baseline/      # 基线检查模块
│       ├── collection/    # 信息采集模块
│       ├── inventory_converter/  # Inventory转换模块
│       ├── itsm/          # ITSM流程处理模块
│       ├── processing/    # 数据处理模块
│       └── web_app/       # Web应用模块
└── tests/                 # 测试目录
```

## 安装指南

1. 克隆项目到本地
2. 创建虚拟环境: `python -m venv .venv`
3. 激活虚拟环境: `source .venv/bin/activate` (Linux/Mac) 或 `.venv\Scripts\activate` (Windows)
4. 安装依赖: `pip install -r requirements.txt`

## 使用方法

### 基线检查功能

基线检查功能用于检查网络设备的配置是否符合安全基线要求。

使用方法:
```bash
python main.py --action baseline
```

该功能会:
1. 读取设备清单文件
2. 连接到每个设备
3. 收集设备配置信息
4. 根据基线规则检查配置
5. 生成检查报告

### 从Excel生成设备Inventory文件

该功能可以从Excel文件生成设备Inventory文件。

使用方法:
```bash
python scripts/generate_inventory_from_yaml.py
```

输入文件: `data/input/inventory/hosts.yaml`
输出文件: 
- `data/input/inventory/hosts_{timestamp}.yaml`
- `data/input/inventory/groups_{timestamp}.yaml`
- `data/input/inventory/default_{timestamp}.yaml`

## 注意事项

1. 确保配置文件路径正确
2. 确保设备可以正常连接
3. 定期更新基线规则文件