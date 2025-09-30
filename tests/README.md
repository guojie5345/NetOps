# 测试目录说明

本目录包含项目的所有测试脚本和测试配置文件。

## 目录结构

```
tests/
├── test_all_functions.py       # 测试所有功能的脚本
├── test_api_only.py            # 测试仅有API端点的情况
├── test_baseline.py            # 测试基线检查功能
├── test_collection.py          # 测试信息采集功能
├── test_longest_prefix.py      # 测试最长前缀匹配算法
├── test_ssh_config.json        # SSH测试配置文件
└── test_collection_config.json # 信息采集测试配置文件
```

## 运行测试

### 运行所有测试

```bash
cd tests
python test_all_functions.py
```

### 运行单个测试

```bash
cd tests
python test_collection.py
python test_baseline.py
python test_api_only.py
python test_longest_prefix.py
```

## 测试配置文件

- `test_ssh_config.json`: SSH连接测试配置
- `test_collection_config.json`: 信息采集测试配置

这些配置文件包含测试设备的信息，用于执行各种功能测试。