# 自动化运维工具

# -*- coding: utf-8 -*-

## 项目概述
自动化运维工具是一个Python项目，用于简化运维任务，提高效率。该工具能够自动化IT服务管理(ITSM)的变更流程，包括信息采集、处理、配置生成等功能。

## 功能特点
1. **自动部署**：自动部署应用程序到目标服务器
2. **信息采集**：利用设备API或SSH方式采集设备信息
3. **信息处理**：将采集后的信息转换为可用于后续处理的格式
4. **配置生成**：通过配置模板，生成最终的配置文件
5. **配置管理**：利用配置文件管理应用程序的配置信息
6. **基线检查**：检查网络设备配置是否符合安全基线要求
7. **自动备份**：自动备份数据库和文件（暂停开发）
8. **自动监控**：自动监控服务器和应用程序的运行状态（暂停开发）
9. **自动报警**：自动报警当服务器或应用程序出现问题时（暂停开发）

## 技术栈
- **编程语言**：Python 3.12
- **依赖库**：
  - requests: 用于发送HTTP请求和API调用
  - pytest: 用于编写和运行测试用例
  - netmiko: 用于SSH连接和配置设备
  - jinja2: 用于模板渲染
  - selenium: 用于浏览器自动化测试
  - openpyxl: 用于读写Excel文件
  - pandas: 用于数据处理和分析
  - mysql-connector-python: 用于连接和操作MySQL数据库
  - sendgrid: 用于发送邮件

## 目录结构
```
变更自动化/
├── .gitignore              # Git忽略文件
├── .idea/                  # IDE配置文件
├── .trae/                  # Trae配置文件
├── README.md               # 项目说明文档
├── main.py                 # 主程序入口
├── project_organization.md # 项目组织优化建议
├── requirements.txt        # 依赖包列表
├── setup_guide.md          # 安装设置指南
├── src/                    # 源代码目录
│   ├── __init__.py         # 包初始化文件
│   ├── core/               # 核心功能模块
│   │   └── config_manager.py # 配置管理类
│   ├── modules/            # 各功能模块
│   │   ├── ali_cloud_apis/ # 阿里云API模块
│   │   ├── collection/     # 信息采集模块
│   │   ├── configuration/  # 配置生成模块
│   │   ├── deployment/     # 自动部署模块
│   │   ├── itsm/           # ITSM模块
│   │   ├── management/     # 配置管理模块
│   │   └── processing/     # 信息处理模块
│   ├── utils/              # 通用工具函数
│   │   └── logger.py       # 日志工具
│   └── config/             # 配置文件
│       └── config.json     # 配置文件
├── tests/                  # 测试代码
├── docs/                   # 文档
│   └── README.md           # 文档目录说明
├── scripts/                # 脚本工具
│   ├── install_linux.sh    # Linux安装脚本
│   └── install_windows.bat # Windows安装脚本
├── templates/              # 模板文件
│   ├── hillstone/          # Hillstone模板
│   └── *.xlsx              # Excel模板
├── data/                   # 数据存储
│   ├── input/              # 输入数据
│   │   ├── order/          # 订单数据
│   │   └── test_order/     # 测试订单
│   └── output/             # 输出数据
│       └── change_scripts/ # 变更脚本
├── packages/               # 依赖包存储
│   ├── win_packages/       # Windows依赖包
│   └── linux_packages/     # Linux依赖包
├── logs/                   # 日志文件
└── .venv/                  # Python虚拟环境
```

## 安装指南
1. **克隆项目**
   ```bash
   git clone https://github.com/yourusername/automation-tool.git
   cd automation-tool
   ```

2. **使用安装脚本**
   - Windows:
     ```bash
     scripts\install_windows.bat
     ```
   - Linux:
     ```bash
     chmod +x scripts/install_linux.sh
     ./scripts/install_linux.sh
     ```

3. **手动安装（可选）**
   - 创建虚拟环境
     ```bash
     python -m venv venv
     ```
   - 激活虚拟环境
     - Windows:
       ```bash
       venv\Scripts\activate
       ```
     - Linux/Mac:
       ```bash
       source venv/bin/activate
       ```
   - 安装依赖包
     ```bash
     pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
     ```

## 使用方法
1. 按照`setup_guide.md`配置相关参数
2. 运行主程序
   ```bash
   python main.py --action process --order data/input/orders/your_order_file.xlsx
   ```
3. 运行基线检查
   ```bash
   python main.py --action baseline
   ```
4. 查看运行结果和日志

### 基线检查功能
基线检查功能用于检查网络设备配置是否符合安全基线要求。该功能支持多种设备平台（Cisco、华为、H3C等），可以检查配置合规性、接口状态和系统服务状态。

**功能特点**：
- 支持多种设备平台（Cisco IOS/NX-OS、华为VRP、H3C Comware等）
- 可配置的基线规则（通过`src/config/baseline_rules.yaml`文件）
- 生成HTML和Excel格式的检查报告
- 支持并行检查多台设备

**配置文件**：
- `src/config/baseline_rules.yaml` - 基线检查规则定义文件
- `src/config/ssh_config.json` - SSH设备连接配置文件

**生成的报告**：
- HTML格式报告：`reports/baseline_report_YYYYMMDD_HHMMSS.html`
- Excel格式报告：`reports/baseline_report_YYYYMMDD_HHMMSS.xlsx`

### 从Excel生成设备Inventory文件
除了主程序外，项目还包含一个专门用于从Excel生成网络设备登录inventory文件的脚本。

**功能说明**：
- 从Excel文件读取网络设备配置信息（IP地址、主机名、端口等）
- 智能过滤，只包含有效IP地址且状态为'启用'的设备
- 自动识别设备类型（如Cisco、Huawei等）
- 生成多种格式的inventory文件：完整JSON、简化JSON、INI格式和YAML格式

该功能已被重构为项目的一个正式模块，位于 `src/modules/inventory_converter` 目录下。

**使用方法**：
1. 确保Excel文件放在`data/input/`目录下
2. 运行脚本
   ```bash
   python excel_to_inventory.py
   ```
3. 生成的inventory文件将保存在`data/output/inventory/`目录下，文件名包含时间戳

**生成的文件格式**：
- `inventory_YYYYMMDD_HHMMSS.json` - 完整JSON格式
- `inventory_simple_YYYYMMDD_HHMMSS.json` - 简化JSON格式
- `inventory_YYYYMMDD_HHMMSS.ini` - INI格式
- `hosts_YYYYMMDD_HHMMSS.yaml` - YAML格式的主机文件
- `groups_YYYYMMDD_HHMMSS.yaml` - YAML格式的组文件
- `default_YYYYMMDD_HHMMSS.yaml` - YAML格式的默认配置文件
- `config_YYYYMMDD_HHMMSS.yaml` - YAML格式的配置文件

**模块结构**
Excel到Inventory转换模块采用了标准的Python包结构，主要组件包括：
- `__init__.py`: 包初始化文件，导出主要类
- `excel_to_inventory.py`: 核心转换逻辑实现

## 注意事项
- 确保使用Python 3.11版本
- 开发系统为Windows，测试环境为Linux
- 自动备份、自动监控、自动报警模块应暂停开发
- 所有依赖包应使用清华源进行下载
- 按照`setup_guide.md`完成初始设置

## 贡献指南
1.  Fork 项目
2.  创建特性分支
3.  提交更改
4.  推送到分支
5.  创建Pull Request

## 许可证
[MIT License](LICENSE)