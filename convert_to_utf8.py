#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件编码转换脚本
将项目中非UTF-8编码的文本文件安全转换为UTF-8编码
"""

import os
import shutil
import chardet
from pathlib import Path

def is_binary_file(file_path):
    """
    判断文件是否为二进制文件
    """
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
            if b'\x00' in chunk:  # 如果包含空字节，则很可能是二进制文件
                return True
            # 检查是否包含非文本字符
            text_chars = bytearray({7,8,9,10,12,13,27} | set(range(0x20, 0x100)) - {0x7f})
            return bool(chunk.translate(None, text_chars))
    except:
        return True

def detect_encoding(file_path):
    """
    检测文件编码
    """
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            return result['encoding'], result['confidence']
    except Exception as e:
        return f"Error: {str(e)}", 0.0

def convert_file_to_utf8(file_path, source_encoding):
    """
    将文件转换为UTF-8编码
    使用安全的方式：先创建新文件，再替换原文件
    """
    try:
        # 读取原文件内容
        with open(file_path, 'r', encoding=source_encoding, errors='ignore') as f:
            content = f.read()
        
        # 创建临时文件路径
        temp_file_path = file_path + '.tmp'
        
        # 将内容写入新的UTF-8编码文件
        with open(temp_file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 替换原文件
        shutil.move(temp_file_path, file_path)
        
        return True, f"成功转换文件 {file_path} 从 {source_encoding} 到 UTF-8"
    except Exception as e:
        # 如果转换失败，删除临时文件
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        return False, f"转换文件 {file_path} 失败: {str(e)}"

def should_exclude_directory(dir_path):
    """
    判断是否应该排除该目录
    """
    dir_name = os.path.basename(dir_path)
    # 排除所有以.开头的目录
    if dir_name.startswith('.'):
        return True
    # 排除特定的缓存或临时目录
    exclude_dirs = ['__pycache__', 'node_modules']
    if dir_name in exclude_dirs:
        return True
    return False

def convert_project_to_utf8(project_path):
    """
    转换项目中所有非UTF-8编码的文件为UTF-8编码
    """
    conversion_log = []
    
    for root, dirs, files in os.walk(project_path):
        # 过滤需要排除的目录
        dirs[:] = [d for d in dirs if not should_exclude_directory(os.path.join(root, d))]
        
        for file in files:
            file_path = os.path.join(root, file)
            
            # 跳过二进制文件
            if is_binary_file(file_path):
                conversion_log.append({
                    'file': file_path,
                    'status': 'Skipped',
                    'message': 'Binary file'
                })
                continue
            
            # 检测文件编码
            encoding, confidence = detect_encoding(file_path)
            
            # 如果已经是UTF-8编码，则跳过
            if encoding and (encoding.lower() == 'utf-8' or encoding.lower() == 'utf-8-sig'):
                conversion_log.append({
                    'file': file_path,
                    'status': 'Skipped',
                    'message': f'Already UTF-8 ({encoding})'
                })
                continue
            
            # 转换文件
            if encoding:
                success, message = convert_file_to_utf8(file_path, encoding)
                conversion_log.append({
                    'file': file_path,
                    'status': 'Success' if success else 'Failed',
                    'message': message,
                    'original_encoding': encoding
                })
            else:
                conversion_log.append({
                    'file': file_path,
                    'status': 'Failed',
                    'message': '无法检测文件编码',
                    'original_encoding': 'Unknown'
                })
    
    return conversion_log

def save_conversion_log(log, output_file):
    """
    保存转换日志到文件
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# 项目文件编码转换日志\n\n")
        f.write("| 文件路径 | 状态 | 原始编码 | 消息 |\n")
        f.write("|----------|------|----------|------|\n")
        
        for item in log:
            original_encoding = item.get('original_encoding', 'N/A')
            f.write(f"| {item['file']} | {item['status']} | {original_encoding} | {item['message']} |\n")
        
        # 统计信息
        total_files = len(log)
        success_count = len([l for l in log if l['status'] == 'Success'])
        failed_count = len([l for l in log if l['status'] == 'Failed'])
        skipped_count = len([l for l in log if l['status'] == 'Skipped'])
        
        f.write("\n## 转换统计\n\n")
        f.write(f"- 总文件数: {total_files}\n")
        f.write(f"- 成功转换: {success_count}\n")
        f.write(f"- 转换失败: {failed_count}\n")
        f.write(f"- 跳过文件: {skipped_count}\n")

def main():
    project_path = os.path.dirname(os.path.abspath(__file__))
    print(f"开始转换项目路径: {project_path}")
    
    # 执行转换
    log = convert_project_to_utf8(project_path)
    
    # 保存日志
    log_file = os.path.join(project_path, 'conversion_log.md')
    save_conversion_log(log, log_file)
    
    print(f"转换日志已保存到: {log_file}")
    
    # 打印转换结果
    success_count = len([l for l in log if l['status'] == 'Success'])
    failed_count = len([l for l in log if l['status'] == 'Failed'])
    
    print(f"\n转换完成:")
    print(f"  成功转换: {success_count} 个文件")
    print(f"  转换失败: {failed_count} 个文件")
    
    if failed_count > 0:
        print("\n转换失败的文件:")
        for item in log:
            if item['status'] == 'Failed':
                print(f"  {item['file']}: {item['message']}")

if __name__ == "__main__":
    main()