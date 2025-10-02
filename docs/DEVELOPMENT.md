# ITSM变更自动化工具开发指南

## 项目概述

ITSM变更自动化工具是一个用于自动化IT服务管理(ITSM)中变更流程的Python项目。它能够自动部署应用程序到目标服务器，采集设备信息，处理采集的数据，生成配置文件，并管理应用程序的配置。

## 技术栈

- **编程语言**: Python 3.12
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

## 详细目录结构

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

## 功能模块

### 1. 基线检查模块 (src/modules/baseline)

实现网络设备配置基线检查功能，支持多种设备平台。

主要文件：
- `check_baseline.py` - 基线检查核心逻辑
- `generate_summary_report.py` - 生成汇总报告

### 2. 信息采集模块 (src/modules/collection)

通过SSH或API方式采集设备信息。

### 3. 数据处理模块 (src/modules/processing)

处理采集到的数据，转换为可用格式。

### 4. Inventory转换模块 (src/modules/inventory_converter)

将Excel格式的设备信息转换为Inventory文件。

### 5. ITSM流程处理模块 (src/modules/itsm)

处理ITSM工单，与ITSM系统交互。

### 6. API相关模块 (src/modules/apis)

处理与各种API的交互。

### 7. Web应用模块 (src/modules/web_app)

提供Web界面用于查看报告和管理配置。

## 依赖管理注意事项

1. 所有依赖包应使用清华源进行下载
2. 定期更新依赖包版本
3. 分离开发依赖和生产依赖
4. 使用虚拟环境隔离依赖

## 开发环境设置

1. 克隆项目到本地
2. 创建虚拟环境: `python -m venv .venv`
3. 激活虚拟环境: `source .venv/bin/activate` (Linux/Mac) 或 `.venv\Scripts\activate` (Windows)
4. 安装依赖: `pip install -r requirements.txt -r requirements-dev.txt`