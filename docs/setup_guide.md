# ITSM变更自动化工具设置指南

## 项目结构优化说明

为了使项目更加整洁有序，我们已经创建了新的目录结构。由于系统权限限制，部分现有目录无法自动移动，需要手动完成。

## 手动移动目录步骤

1. **移动ITSM目录**
   - 将 `e:/Development/Python/变更自动化/ITSM` 目录移动到 `e:/Development/Python/变更自动化/src/modules/itsm`
   - 注意：移动后目录名称应改为小写 `itsm`

2. **移动ali_cloud_apis目录**
   - 将 `e:/Development/Python/变更自动化/ali_cloud_apis` 目录移动到 `e:/Development/Python/变更自动化/src/modules/ali_cloud_apis`

3. **移动模板文件**
   - 将 `src/modules/itsm/templates` 目录中的所有文件移动到 `e:/Development/Python/变更自动化/templates`

4. **移动测试订单**
   - 将 `src/modules/itsm/test_order` 目录中的所有文件移动到 `e:/Development/Python/变更自动化/data/input/orders`

## 剩余设置步骤

1. **创建配置文件**
   - 在 `src/config` 目录下创建 `config.json` 文件
   - 参考以下示例配置：
   ```json
   {
     "aliyun": {
       "access_key": "your_access_key",
       "secret_key": "your_secret_key",
       "region_id": "your_region_id"
     },
     "itsm": {
       "url": "https://itsm.example.com/api",
       "username": "your_username",
       "password": "your_password"
     },
     "templates": {
       "path": "templates/"
     }
   }
   ```

2. **创建日志工具**
   - 在 `src/utils` 目录下创建 `logger.py` 文件
   - 示例内容：
   ```python
   import logging
   import os
   from logging.handlers import RotatingFileHandler

   def setup_logger():
       """设置日志系统"""
       log_dir = 'logs'
       if not os.path.exists(log_dir):
           os.makedirs(log_dir)

       log_file = os.path.join(log_dir, 'itsm_automation.log')

       # 配置日志格式
       log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
       date_format = '%Y-%m-%d %H:%M:%S'

       # 设置根日志器
       logger = logging.getLogger()
       logger.setLevel(logging.INFO)

       # 控制台日志处理器
       console_handler = logging.StreamHandler()
       console_handler.setFormatter(logging.Formatter(log_format, date_format))
       logger.addHandler(console_handler)

       # 文件日志处理器
       file_handler = RotatingFileHandler(
           log_file,
           maxBytes=1024 * 1024 * 10,  # 10MB
           backupCount=5
       )
       file_handler.setFormatter(logging.Formatter(log_format, date_format))
       logger.addHandler(file_handler)

       return logger
   ```

3. **创建配置管理类**
   - 在 `src/core` 目录下创建 `config_manager.py` 文件
   - 示例内容：
   ```python
   import json
   import os

   class ConfigManager:
       """配置管理类"""
       def __init__(self, config_path):
           """初始化配置管理器

           Args:
               config_path: 配置文件路径
           """
           self.config_path = config_path
           self.config = {}

       def load_config(self):
           """加载配置文件

           Returns:
               dict: 配置字典
           """
           if not os.path.exists(self.config_path):
               raise FileNotFoundError(f'配置文件不存在: {self.config_path}')

           with open(self.config_path, 'r', encoding='utf-8') as f:
               self.config = json.load(f)

           return self.config

       def save_config(self, config=None):
           """保存配置文件

           Args:
               config: 配置字典，如果为None则保存当前配置
           """
           if config is not None:
               self.config = config

           with open(self.config_path, 'w', encoding='utf-8') as f:
               json.dump(self.config, f, ensure_ascii=False, indent=2)

           return True
   ```

## 如何运行项目

1. **安装依赖**
   - Windows: 运行 `scripts/install_windows.bat`
   - Linux: 运行 `scripts/install_linux.sh`

2. **运行主程序**
   ```bash
   cd src
   python main.py --action process --order data/input/orders/your_order_file.xlsx
   ```

3. **运行Inventory转换工具**
   项目包含一个专门用于从Excel生成网络设备登录inventory文件的工具，支持多种输出格式：
   - JSON格式（完整和简化版本）
   - INI格式
   - YAML格式（兼容Netmiko配置）
   
   运行方法：
   ```bash
   python excel_to_inventory.py
   ```
   
   生成的文件将保存在`data/output/inventory/`目录下，包括：
   - `inventory_YYYYMMDD_HHMMSS.json` - 完整JSON格式
   - `inventory_simple_YYYYMMDD_HHMMSS.json` - 简化JSON格式
   - `inventory_YYYYMMDD_HHMMSS.ini` - INI格式
   - `hosts_YYYYMMDD_HHMMSS.yaml` - YAML格式的主机文件
   - `groups_YYYYMMDD_HHMMSS.yaml` - YAML格式的组文件
   - `default_YYYYMMDD_HHMMSS.yaml` - YAML格式的默认配置文件
   - `config_YYYYMMDD_HHMMSS.yaml` - YAML格式的配置文件

## 环境设置（推荐方式）

为了简化环境设置过程，我们提供了专门的批处理脚本：

1. **重置环境**
   - 运行 `reset_environment.bat` 来重新创建整个开发环境
   - 该脚本会自动创建虚拟环境、安装依赖包等

2. **启动CMD环境**
   - 运行 `start_cmd.bat` 来启动配置好的CMD开发环境
   - 该脚本会自动激活虚拟环境并设置工作目录

详细说明请查看项目根目录下的 `ENVIRONMENT_SETUP.md` 文件。

## 如何测试项目

1. **运行单元测试**
   ```bash
   pytest tests/
   ```

2. **手动测试功能**
   - 使用命令行参数测试不同功能
   - 检查输出文件和日志

## 注意事项

1. 确保已安装Python 3.12
2. 在Windows上运行时可能需要以管理员身份执行脚本
3. 如果遇到权限问题，请检查文件和目录的权限设置
4. 7/8/9模块(自动备份、自动监控、自动报警)应暂停开发
5. 所有依赖包应使用清华源进行下载

按照以上步骤完成设置后，项目将按照新的结构组织，更加整洁有序，便于后续开发和维护。