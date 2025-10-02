# ITSM变更自动化工具安装设置指南

## 项目结构优化说明

项目已进行结构优化，将配置文件迁移到`config`目录下，并按功能分类：

```
config/
├── device/            # 设备相关配置
├── itsm/              # ITSM相关配置
└── rule/              # 规则配置文件
```

## 手动移动目录步骤

如果需要手动移动配置文件，请按以下步骤操作：

1. 创建目录结构：
   ```bash
   mkdir -p config/device config/itsm config/rule
   ```

2. 移动设备相关配置文件：
   ```bash
   mv src/config/ssh_config.json config/device/
   mv src/config/device_commands.json config/device/
   mv src/config/device_mapping_config.json config/device/
   ```

3. 移动ITSM相关配置文件：
   ```bash
   mv src/config/api_config.json config/itsm/
   mv src/config/config.json config/itsm/
   mv src/config/scenario_config.json config/itsm/
   ```

4. 移动规则配置文件：
   ```bash
   mv src/config/baseline_rules.yaml config/rule/
   mv src/config/remediation_suggestions.yaml config/rule/
   ```

## 剩余设置步骤

1. 更新配置文件中的路径引用
2. 验证所有功能模块是否正常工作
3. 更新相关文档中的路径引用

## 运行项目

### 环境设置

推荐使用Python虚拟环境：

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 运行基线检查功能

```bash
python main.py --action baseline
```

### 运行Excel转Inventory功能

```bash
python scripts/generate_inventory_from_yaml.py
```

## 注意事项

1. 确保配置文件路径正确
2. 确保设备可以正常连接
3. 定期更新基线规则文件
4. 所有配置文件已迁移至`config`目录，请使用新路径