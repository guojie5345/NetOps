#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件编码检测脚本
用于检测项目中所有文件的编码格式
"""

import os
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

def scan_project_encoding(project_path):
    """
    扫描项目中所有文件的编码
    """
    encoding_report = []
    
    for root, dirs, files in os.walk(project_path):
        # 过滤需要排除的目录
        dirs[:] = [d for d in dirs if not should_exclude_directory(os.path.join(root, d))]
        
        for file in files:
            file_path = os.path.join(root, file)
            
            # 跳过二进制文件
            if is_binary_file(file_path):
                encoding_report.append({
                    'file': file_path,
                    'encoding': 'Binary',
                    'confidence': 1.0,
                    'status': 'Skipped'
                })
                continue
            
            # 检测文本文件编码
            encoding, confidence = detect_encoding(file_path)
            status = 'OK' if encoding == 'utf-8' or encoding == 'UTF-8' else 'Needs Conversion'
            
            encoding_report.append({
                'file': file_path,
                'encoding': encoding,
                'confidence': confidence,
                'status': status
            })
    
    return encoding_report

def save_encoding_report(report, output_file):
    """
    保存编码报告到文件
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# 项目文件编码报告\n\n")
        f.write("| 文件路径 | 编码 | 置信度 | 状态 |\n")
        f.write("|----------|------|--------|------|\n")
        
        for item in report:
            f.write(f"| {item['file']} | {item['encoding']} | {item['confidence']:.2f} | {item['status']} |\n")
        
        # 统计信息
        total_files = len(report)
        utf8_files = len([r for r in report if r['encoding'].lower() == 'utf-8'])
        binary_files = len([r for r in report if r['encoding'] == 'Binary'])
        need_conversion = len([r for r in report if r['status'] == 'Needs Conversion'])
        
        f.write("\n## 统计信息\n\n")
        f.write(f"- 总文件数: {total_files}\n")
        f.write(f"- UTF-8编码文件数: {utf8_files}\n")
        f.write(f"- 二进制文件数: {binary_files}\n")
        f.write(f"- 需要转换的文件数: {need_conversion}\n")

def main():
    project_path = os.path.dirname(os.path.abspath(__file__))
    print(f"正在扫描项目路径: {project_path}")
    
    # 生成编码报告
    report = scan_project_encoding(project_path)
    
    # 保存报告
    report_file = os.path.join(project_path, 'encoding_report.md')
    save_encoding_report(report, report_file)
    
    print(f"编码报告已保存到: {report_file}")
    
    # 打印需要转换的文件
    need_conversion = [r for r in report if r['status'] == 'Needs Conversion']
    if need_conversion:
        print("\n需要转换为UTF-8的文件:")
        for item in need_conversion:
            print(f"  {item['file']} ({item['encoding']})")
    else:
        print("\n没有需要转换的文件。")

if __name__ == "__main__":
    main()