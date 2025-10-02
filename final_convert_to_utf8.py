#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终转换脚本，用于将项目中所有非UTF-8编码的文件转换为UTF-8编码
"""

import os
import shutil
from chardet import detect

# 需要排除的目录（包含"."的目录）
EXCLUDED_DIRS = {'.', '.git', '.vscode', '.idea', '__pycache__', '.pytest_cache'}

# 需要排除的文件扩展名（二进制文件）
BINARY_EXTENSIONS = {
    '.xlsx', '.xls', '.doc', '.docx', '.pdf', '.png', '.jpg', '.jpeg', '.gif', 
    '.bmp', '.ico', '.exe', '.dll', '.so', '.dylib', '.bin', '.zip', '.rar', 
    '.7z', '.tar', '.gz', '.bz2', '.mp3', '.mp4', '.avi', '.mkv', '.mov',
    '.pyc', '.class', '.o', '.obj', '.lib', '.a', '.db', '.sqlite', '.db3',
    '.jar', '.war', '.ear', '.apk', '.ipa', '.dmg', '.iso', '.img', '.bak'
}

def is_binary_file(file_path):
    """判断文件是否为二进制文件"""
    _, ext = os.path.splitext(file_path)
    return ext.lower() in BINARY_EXTENSIONS

def is_excluded_dir(dir_path):
    """判断目录是否需要排除"""
    dir_name = os.path.basename(dir_path)
    return any(excluded_dir in dir_name for excluded_dir in EXCLUDED_DIRS)

def get_file_encoding(file_path):
    """检测文件编码"""
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            result = detect(raw_data)
            return result['encoding']
    except Exception as e:
        print(f"检测文件编码时出错 {file_path}: {e}")
        return None

def convert_file_to_utf8(file_path, encoding):
    """将文件转换为UTF-8编码"""
    try:
        # 读取原文件内容
        with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
            content = f.read()
        
        # 创建临时文件
        temp_file_path = file_path + '.tmp'
        
        # 以UTF-8编码写入临时文件
        with open(temp_file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 替换原文件
        shutil.move(temp_file_path, file_path)
        
        return True
    except Exception as e:
        print(f"转换文件时出错 {file_path}: {e}")
        # 如果转换失败，删除临时文件
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        return False

def main():
    """主函数"""
    project_path = os.path.dirname(os.path.abspath(__file__))
    print(f"开始最终转换项目路径: {project_path}")
    
    success_count = 0
    fail_count = 0
    
    # 遍历项目目录
    for root, dirs, files in os.walk(project_path):
        # 排除特定目录
        dirs[:] = [d for d in dirs if not is_excluded_dir(os.path.join(root, d))]
        
        for file in files:
            file_path = os.path.join(root, file)
            
            # 跳过二进制文件
            if is_binary_file(file_path):
                continue
            
            # 检测文件编码
            encoding = get_file_encoding(file_path)
            if encoding is None:
                fail_count += 1
                continue
            
            # 如果不是UTF-8编码，则进行转换
            if encoding.lower() not in ['utf-8', 'ascii']:
                if convert_file_to_utf8(file_path, encoding):
                    print(f"成功转换: {file_path}")
                    success_count += 1
                else:
                    print(f"转换失败: {file_path}")
                    fail_count += 1
            # 对于ASCII编码的文件，也进行转换以确保统一性
            elif encoding.lower() == 'ascii':
                if convert_file_to_utf8(file_path, encoding):
                    print(f"成功转换 (ASCII): {file_path}")
                    success_count += 1
                else:
                    print(f"转换失败 (ASCII): {file_path}")
                    fail_count += 1
    
    print(f"\n最终转换完成:")
    print(f"  成功转换: {success_count} 个文件")
    print(f"  转换失败: {fail_count} 个文件")

if __name__ == "__main__":
    main()