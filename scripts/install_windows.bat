@echo off

:: 设置中文编码
chcp 65001 > nul

:: 检查Python版本
python --version 2>NUL
if %ERRORLEVEL% NEQ 0 (
    echo 未找到Python，请先安装Python 3.12
    pause
    exit /b 1
)

:: 检查Python版本是否为3.12
for /f "tokens=2 delims=." %%i in ('python --version 2^>^&1') do (
    set PYTHON_VERSION=%%i
)
if not "%PYTHON_VERSION%" == "12" (
    echo 请使用Python 3.12版本
    pause
    exit /b 1
)

:: 创建虚拟环境
echo 创建虚拟环境...
python -m venv venv
if %ERRORLEVEL% NEQ 0 (
    echo 创建虚拟环境失败
    pause
    exit /b 1
)

:: 激活虚拟环境
echo 激活虚拟环境...
call venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo 激活虚拟环境失败
    pause
    exit /b 1
)

:: 安装依赖包
echo 安装依赖包...
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
if %ERRORLEVEL% NEQ 0 (
    echo 安装依赖包失败
    pause
    exit /b 1
)

:: 下载Windows平台依赖包到packages/win_packages
echo 下载Windows平台依赖包...
mkdir packages\win_packages 2>NUL
pip download -d packages\win_packages -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
if %ERRORLEVEL% NEQ 0 (
    echo 下载Windows依赖包失败
    pause
    exit /b 1
)

echo 安装完成！
pause