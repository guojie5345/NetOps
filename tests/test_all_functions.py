#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试所有功能的脚本
"""

import subprocess
import sys
import os

def run_command(command, description, cwd=None):
    """运行命令并返回结果"""
    print(f"\n{'='*50}")
    print(f"正在执行: {description}")
    print(f"命令: {command}")
    print(f"{'='*50}")
    
    # 如果未指定cwd，则使用当前工作目录
    if cwd is None:
        cwd = os.getcwd()
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=cwd)
        print(f"返回码: {result.returncode}")
        if result.stdout:
            print(f"输出:\n{result.stdout}")
        if result.stderr:
            print(f"错误:\n{result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"执行命令时出错: {e}")
        return False

def main():
    """主函数"""
    print("开始测试所有功能...")
    
    # 获取项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 测试信息采集功能
    success = run_command("python main.py --action collect", "信息采集功能", project_root)
    if not success:
        print("信息采集功能测试失败")
        return False
    
    # 测试基线检查功能
    success = run_command("python main.py --action baseline", "基线检查功能", project_root)
    if not success:
        print("基线检查功能测试失败")
        return False
    
    print(f"\n{'='*50}")
    print("所有功能测试完成!")
    print(f"{'='*50}")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)