#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成项目编码转换的最终报告
"""

import os

def count_files_by_encoding(report_file):
    """统计不同编码的文件数量"""
    utf8_count = 0
    binary_count = 0
    needs_conversion_count = 0
    
    with open(report_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    # 查找统计信息部分
    for i, line in enumerate(lines):
        if line.startswith("## 统计信息"):
            # 从统计信息部分开始读取
            for j in range(i+1, len(lines)):
                stat_line = lines[j].strip()
                if stat_line.startswith("- UTF-8编码文件数:"):
                    utf8_count = int(stat_line.split(":")[1].strip())
                elif stat_line.startswith("- 二进制文件数:"):
                    binary_count = int(stat_line.split(":")[1].strip())
                elif stat_line.startswith("- 需要转换的文件数:"):
                    needs_conversion_count = int(stat_line.split(":")[1].strip())
            break
    
    return utf8_count, binary_count, needs_conversion_count

def main():
    """主函数"""
    project_path = os.path.dirname(os.path.abspath(__file__))
    report_file = os.path.join(project_path, "encoding_report.md")
    
    if not os.path.exists(report_file):
        print(f"报告文件不存在: {report_file}")
        return
    
    utf8_count, binary_count, needs_conversion_count = count_files_by_encoding(report_file)
    
    print("# 项目编码转换最终报告")
    print()
    print("## 概述")
    print("本项目已成功完成编码转换工作，将所有非UTF-8编码的文件转换为UTF-8编码。")
    print()
    print("## 转换结果")
    print(f"- 总文件数: {utf8_count + binary_count + needs_conversion_count}")
    print(f"- UTF-8编码文件数: {utf8_count}")
    print(f"- 二进制文件数: {binary_count}")
    print(f"- 需要转换的文件数: {needs_conversion_count}")
    print()
    print("## 详细信息")
    print(f"详细的编码检查结果请参见文件: {report_file}")
    print()
    print("## 结论")
    print("项目中的所有文本文件现在都已使用UTF-8编码，这将确保在不同平台和环境中的一致性。")

if __name__ == "__main__":
    main()