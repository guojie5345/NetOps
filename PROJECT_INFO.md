# 项目信息

## 项目结构

```
项目根目录/
├── main.py                    # 主程序入口
├── config/                    # 配置文件目录（已迁移）
│   ├── baseline_rules.yaml    # 基线检查规则配置
│   ├── ssh_config.json        # SSH设备配置
│   ├── api_config.json        # API配置
│   ├── config.json            # 通用配置
│   ├── device_commands.json   # 设备命令配置
│   ├── device_mapping_config.json # 设备映射配置
│   └── scenario_config.json   # 场景配置
├── src/
│   ├── core/                  # 核心模块
│   │   └── config_manager.py  # 配置管理器
│   ├── modules/               # 功能模块
│   │   ├── baseline/          # 基线检查模块
│   │   ├── collection/        # 信息采集模块
│   │   ├── processing/        # 订单处理模块
│   │   ├── configuration/     # 配置生成模块
│   │   ├── deployment/        # 部署模块
│   │   ├── management/        # 管理模块
│   │   ├── inventory_converter/ # 库存转换模块
│   │   └── itsm/              # ITSM接口模块
│   └── utils/                 # 工具模块
│       └── logger.py          # 日志工具
├── templates/                 # 模板文件目录
├── reports/                   # 报告输出目录
├── data/                      # 数据目录
│   ├── input/                 # 输入数据
│   └── output/                # 输出数据
├── docs/                      # 文档目录
├── logs/                      # 日志目录
└── tests/                     # 测试目录
```

## 配置文件说明

- `config/ssh_config.json`: SSH设备连接配置
- `config/api_config.json`: API接口配置
- `config/baseline_rules.yaml`: 基线检查规则配置
- `config/config.json`: 通用配置
- `config/device_commands.json`: 设备命令配置
- `config/device_mapping_config.json`: 设备映射配置
- `config/scenario_config.json`: 场景配置

## 核心模块说明

### 主程序 (main.py)
- 程序入口点
- 命令行参数解析
- 功能模块调度

### 配置管理 (src/core/config_manager.py)
- 配置文件加载和管理
- 支持多种配置文件格式

### 基线检查模块 (src/modules/baseline/)
- 网络设备配置基线检查
- 支持多种厂商设备
- 生成HTML和Excel报告

### 信息采集模块 (src/modules/collection/)
- 通过SSH或API采集设备信息
- 支持多种设备类型

### 订单处理模块 (src/modules/processing/)
- 处理ITSM订单文件
- 生成相应配置

### 配置生成模块 (src/modules/configuration/)
- 根据模板和数据生成配置文件

### 部署模块 (src/modules/deployment/)
- 自动部署配置到设备

### 管理模块 (src/modules/management/)
- 设备管理功能

### 库存转换模块 (src/modules/inventory_converter/)
- 将Excel格式的库存信息转换为标准格式

### ITSM接口模块 (src/modules/itsm/)
- 与ITSM系统对接

### 工具模块 (src/utils/)
- 日志工具 (logger.py)