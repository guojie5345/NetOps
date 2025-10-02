# ITSM变更自动化工具项目总结

## 项目概述

ITSM变更自动化工具是一个用于自动化IT服务管理(ITSM)中变更流程的Python项目。它能够自动部署应用程序到目标服务器，采集设备信息，处理采集的数据，生成配置文件，并管理应用程序的配置。

## 技术栈

- **编程语言**: Python 3.12.10
- **依赖库**:
  - requests: 用于发送HTTP请求和API调用
  - pytest: 用于编写和运行测试用例
  - netmiko: 用于SSH连接和配置设备
  - jinja2: 用于模板渲染
  - selenium: 用于浏览器自动化测试
  - openpyxl: 用于读写Excel文件
  - pandas: 用于数据处理和分析
  - mysql-connector-python: 用于连接和操作MySQL数据库
  - sendgrid: 用于发送邮件

## 核心功能

### 1. 基线检查功能

基线检查功能用于检查网络设备的配置是否符合安全基线要求。

**功能特点**：
- 支持多种设备平台（Cisco IOS/NX-OS、华为VRP、H3C Comware等）
- 可配置的基线规则（通过`config/rule/baseline_rules.yaml`文件）
- 生成HTML和Excel格式的检查报告
- 支持并行检查多台设备

**配置文件**：
- `config/rule/baseline_rules.yaml` - 基线检查规则定义文件
- `config/device/ssh_config.json` - SSH设备连接配置文件

**生成的报告**：
- HTML格式报告：`reports/baseline_report_YYYYMMDD_HHMMSS.html`
- Excel格式报告：`reports/baseline_report_YYYYMMDD_HHMMSS.xlsx`

### 2. Excel转Inventory功能

从Excel文件生成设备Inventory文件。

**功能说明**：
- 从Excel文件读取网络设备配置信息（IP地址、主机名、端口等）
- 智能过滤，只包含有效IP地址且状态为'启用'的设备
- 自动识别设备类型（如Cisco、Huawei等）
- 生成多种格式的inventory文件：YAML格式

**使用方法**：
1. 确保Excel文件放在`data/input/inventory/`目录下
2. 运行脚本
   ```bash
   python scripts/generate_inventory_from_yaml.py
   ```
3. 生成的inventory文件将保存在`data/input/inventory/`目录下，文件名包含时间戳

**生成的文件格式**：
- `hosts_{timestamp}.yaml` - 主机配置文件
- `groups_{timestamp}.yaml` - 组配置文件
- `default_{timestamp}.yaml` - 默认配置文件

## 项目结构

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

## 配置文件说明

### 1. 基线规则配置文件

- `config/rule/baseline_rules.yaml` - 定义各种设备类型的基线检查规则
- `config/rule/remediation_suggestions.yaml` - 定义不符合基线规则时的修复建议

### 2. 设备连接配置文件

- `config/device/ssh_config.json` - 定义SSH连接设备的参数

### 3. ITSM配置文件

- `config/itsm/itsm_config.json` - 定义ITSM系统的连接参数

## 核心模块说明

### 1. 基线检查模块 (src/modules/baseline)

- `check_baseline.py` - 实现基线检查的核心逻辑
- `generate_summary_report.py` - 生成汇总报告

### 2. 信息采集模块 (src/modules/collection)

- 实现基于API和SSH的信息采集功能

### 3. Inventory转换模块 (src/modules/inventory_converter)

- 实现从Excel到YAML格式Inventory文件的转换

### 4. ITSM模块 (src/modules/itsm)

- 实现与ITSM系统的交互功能

### 5. 数据处理模块 (src/modules/processing)

- 实现数据处理和转换功能

## 测试

项目使用pytest作为测试框架，测试代码位于`tests/`目录下。

## 部署

项目可以通过Python虚拟环境进行部署，依赖包通过`requirements.txt`进行管理。