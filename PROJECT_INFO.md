# 项目信息汇总

## 项目基本信息
- **项目名称**: 自动化运维工具
- **项目类型**: Python 项目
- **主要功能**: 
  1. 自动部署：自动部署应用程序到目标服务器
  2. 信息采集：利用设备API或SSH方式采集设备信息
  3. 信息处理：将采集后的信息转换为可用于后续处理的格式
  4. 配置生成：通过配置模板，将处理后的信息运用到配置模板中，生成最终的配置文件
  5. 配置管理：利用配置文件管理应用程序的配置信息
  6. 基线检查：检查网络设备配置是否符合安全基线要求
  7. 自动备份：自动备份数据库和文件（暂停开发）
  8. 自动监控：自动监控服务器和应用程序的运行状态（暂停开发）
  9. 自动报警：自动报警当服务器或应用程序出现问题时（暂停开发）

## 技术栈信息
- **Python版本**: 3.12.10
- **主要依赖库**:
  - requests: 用于发送 HTTP 请求和API调用
  - pytest: 用于编写和运行测试用例
  - netmiko (4.6.0): 用于SSH连接和配置设备
  - jinja2 (3.1.6): 用于模板渲染
  - selenium: 用于浏览器自动化测试
  - openpyxl (3.1.5): 用于读写Excel文件
  - pandas: 数据处理，用于数据处理和分析
  - mysql-connector-python: 数据库操作，用于连接和操作MySQL数据库
  - sendgrid: 邮件发送，用于发送邮件
  - PyYAML (6.0.2): 用于处理YAML配置文件
  - paramiko (4.0.0): SSH连接库

## 项目结构
```
项目根目录/
├── main.py                    # 主程序入口
├── src/
│   ├── core/                  # 核心模块
│   ├── modules/               # 功能模块
│   │   ├── baseline/          # 基线检查模块
│   │   ├── collection/        # 信息采集模块
│   │   ├── processing/        # 订单处理模块
│   │   ├── configuration/     # 配置生成模块
│   │   ├── deployment/        # 部署模块
│   │   ├── management/        # 管理模块
│   │   ├── inventory_converter/ # 库存转换模块
│   │   └── itsm/              # ITSM接口模块
│   ├── config/                # 配置文件目录
│   │   ├── baseline_rules.yaml # 基线检查规则配置
│   │   ├── ssh_config.json    # SSH设备配置
│   │   ├── api_config.json    # API配置
│   │   └── config.json        # 通用配置
│   └── utils/                 # 工具模块
├── templates/                 # 模板文件目录
├── reports/                   # 报告输出目录
├── data/                      # 数据目录
│   ├── input/                 # 输入数据
│   └── output/                # 输出数据
├── docs/                      # 文档目录
├── logs/                      # 日志目录
└── tests/                     # 测试目录
```

## 核心功能说明

### 1. 基线检查功能
- **功能描述**: 检查网络设备配置是否符合安全基线要求
- **支持平台**: Cisco IOS/NX-OS、华为VRP、H3C Comware等
- **使用方法**: `python main.py --action baseline`
- **报告输出**: HTML和Excel格式报告，保存在reports/目录下

### 2. 信息采集功能
- **功能描述**: 通过SSH或API方式采集设备信息
- **使用方法**: `python main.py --action collect`

### 3. 订单处理功能
- **功能描述**: 处理ITSM订单文件并生成相应配置
- **使用方法**: `python main.py --action process --order <订单文件路径>`

## 配置文件说明
- `src/config/ssh_config.json`: SSH设备连接配置
- `src/config/api_config.json`: API接口配置
- `src/config/baseline_rules.yaml`: 基线检查规则配置
- `src/config/config.json`: 通用配置

## 测试与验证
- 已通过`test_all_functions.py`脚本验证所有功能正常工作
- 基线检查功能已成功集成到主程序中
- HTML和Excel报告均能正确生成并包含详细检查结果