# -*- coding: utf-8 -*-

## 项目概述
自动化运维工具是一个Python项目，用于简化运维任务，提高效率。该工具能够自动化IT服务管理(ITSM)的变更流程，包括但不限于信息采集、处理、配置生成等功能。

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

## 项目目录结构
项目采用模块化结构设计，主要包含以下目录和文件：
- `.gitignore`: Git忽略文件
- `.idea/`: IDE配置文件
- `.trae/`: Trae配置文件
- `README.md`: 项目说明文档
- `main.py`: 主程序入口
- `project_organization.md`: 项目组织优化建议
- `requirements.txt`: 依赖包列表
- `setup_guide.md`: 安装设置指南
- `src/`: 源代码目录
  - `__init__.py`: 包初始化文件
  - `core/`: 核心功能模块
    - `config_manager.py`: 配置管理类
  - `modules/`: 各功能模块
    - `ali_cloud_apis/`: 阿里云API模块
      - `aliyun_api.py`: 实现阿里云API数据获取
    - `collection/`: 信息采集模块
    - `configuration/`: 配置生成模块
    - `deployment/`: 自动部署模块
    - `itsm/`: ITSM模块
      - `itsm.py`: 调用ITSM，完成变更填写
    - `management/`: 配置管理模块
    - `processing/`: 信息处理模块
      - `process_order.py`: 处理用户需求订单，生成配置脚本
  - `utils/`: 通用工具函数
    - `logger.py`: 日志工具
  - `config/`: 配置文件
    - `config.json`: 配置文件
- `tests/`: 测试代码
- `docs/`: 文档
  - `README.md`: 文档目录说明
  - `DEVELOPMENT.md`: 开发文档
- `scripts/`: 脚本工具
  - `install_linux.sh`: Linux安装脚本
  - `install_windows.bat`: Windows安装脚本
- `templates/`: 模板文件
  - `hillstone/`: Hillstone模板
  - `*.xlsx`: Excel模板
- `data/`: 数据存储
  - `input/`: 输入数据
    - `order/`: 订单数据
    - `test_order/`: 测试订单
  - `output/`: 输出数据
    - `change_scripts/`: 变更脚本
- `packages/`: 依赖包存储
  - `win_packages/`: Windows依赖包
  - `linux_packages/`: Linux依赖包
- `logs/`: 日志文件
- `.venv/`: Python虚拟环境
- `task.md`: 项目任务清单与状态跟踪

## 功能模块

### 1. 基础架构搭建
- 项目目录结构设计
- 虚拟环境配置(Python 3.12)
- 依赖包安装与管理
- 版本控制初始化

### 2. 自动部署模块
- 设计部署流程和策略
- 开发应用程序打包功能
- 实现目标服务器连接管理
- 开发文件传输功能
- 实现应用程序安装与启动脚本
- 添加部署结果验证

### 3. 信息采集模块
- 设计设备信息采集接口
- 实现基于API的信息采集功能(使用requests库)
- 实现基于SSH的信息采集功能(使用netmiko库)
- 开发数据存储机制
- 添加采集任务调度功能

### 4. 信息处理模块
- 设计数据转换接口
- 实现原始数据清洗功能
- 开发数据格式化处理功能
- 实现数据标准化功能
- 添加异常数据处理机制

### 5. Excel到设备Inventory转换模块
- 实现Excel文件读取和解析功能(使用pandas和openpyxl库)
- 开发设备信息智能识别功能(IP地址、主机名、端口等)
- 添加数据过滤功能(只包含有效IP地址且状态为'启用'的设备)
- 实现设备类型自动识别功能(支持Cisco、Huawei等常见网络设备)
- 开发多格式inventory文件生成功能(JSON和INI格式)
- 添加结果验证和日志记录

### 5. 配置生成模块
- 设计配置模板系统(使用jinja2库)
- 开发模板管理功能
- 实现数据与模板的绑定功能
- 添加配置文件生成与导出功能
- 实现配置文件验证功能

### 6. 配置管理模块
- 设计配置文件存储结构
- 实现配置文件版本控制
- 开发配置文件比较功能
- 添加配置文件回滚功能
- 实现配置文件导入导出功能

### 7. 自动备份模块(暂停开发)
- 设计备份策略和计划
- 实现数据库备份功能(使用mysql-connector-python库)
- 开发文件系统备份功能
- 添加备份压缩和加密功能
- 实现备份存储管理和清理功能
- 开发备份恢复功能

### 8. 自动监控模块(暂停开发)
- 设计监控指标体系
- 实现服务器资源监控(CPU、内存、磁盘、网络)
- 开发应用程序运行状态监控
- 添加监控数据采集和存储
- 实现监控告警阈值设置

### 9. 自动报警模块(暂停开发)
- 设计告警规则和级别
- 实现邮件报警功能(使用sendgrid库)
- 开发短信或其他通知渠道
- 添加告警确认和处理流程
- 实现告警统计和报表功能

### 10. 测试与质量保障
- 编写单元测试用例(使用pytest库)
- 开发集成测试用例
- 实现自动化测试流程
- 添加代码质量检查
- 开发性能测试功能

### 11. 文档与部署
- 编写用户手册
- 开发API文档
- 编写部署指南
- 添加系统维护文档
- 实现帮助文档集成

## 依赖管理
- **Python版本**: 必须使用Python 3.12
- **虚拟环境**: 建议使用虚拟环境进行开发
- **依赖包下载**: 
  - 需分别下载Windows和Linux平台的依赖包
  - Windows依赖包放置在win_packages文件夹
  - Linux依赖包放置在linux_packages文件夹
  - 所有依赖包应使用清华源进行下载

## 注意事项
1. 前期工作已完成部分功能，包括阿里云API数据获取和ITSM操作
2. 编码过程中应利用已有脚本完成相关功能
3. 7/8/9模块(自动备份、自动监控、自动报警)应暂停开发
4. 所有操作应遵循项目规范和最佳实践