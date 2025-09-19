#!/bin/bash

# 设置中文编码
export LANG="zh_CN.UTF-8"

echo "ITSM变更自动化工具安装脚本（Linux）"

# 检查Python版本
if ! command -v python3 &> /dev/null
then
    echo "未找到Python，请先安装Python 3.12"
    exit 1
fi

# 检查Python版本是否为3.12
PYTHON_VERSION=$(python3 --version | cut -d '.' -f 2)
if [ "$PYTHON_VERSION" != "12" ]
then
    echo "请使用Python 3.12版本"
    exit 1
fi

# 创建虚拟环境
echo "创建虚拟环境..."
python3 -m venv venv
if [ $? -ne 0 ]
then
    echo "创建虚拟环境失败"
    exit 1
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate
if [ $? -ne 0 ]
then
    echo "激活虚拟环境失败"
    exit 1
fi

# 安装依赖包
echo "安装依赖包..."
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
if [ $? -ne 0 ]
then
    echo "安装依赖包失败"
    exit 1
fi

# 下载Linux平台依赖包到packages/linux_packages
echo "下载Linux平台依赖包..."
mkdir -p packages/linux_packages
pip download -d packages/linux_packages -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
if [ $? -ne 0 ]
then
    echo "下载Linux依赖包失败"
    exit 1
fi

echo "安装完成！"