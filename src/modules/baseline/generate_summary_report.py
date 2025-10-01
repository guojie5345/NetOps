#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
汇总报告生成模块
用于从最新的基线检查结果生成汇总报告
"""

import os
import json
import re
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from jinja2 import Template

# 配置日志
logger = logging.getLogger(__name__)

def find_latest_baseline_report() -> Optional[str]:
    """查找最新的基线检查报告
    
    Returns:
        str: 最新基线检查报告的路径，如果未找到则返回None
    """
    reports_dir = 'reports'
    if not os.path.exists(reports_dir):
        logger.warning(f"报告目录 {reports_dir} 不存在")
        return None
        
    # 查找所有基线检查报告文件
    baseline_reports = []
    for filename in os.listdir(reports_dir):
        if filename.startswith('baseline_report_') and filename.endswith('.html'):
            filepath = os.path.join(reports_dir, filename)
            baseline_reports.append((filepath, os.path.getmtime(filepath)))
    
    # 如果没有找到报告文件
    if not baseline_reports:
        logger.warning("未找到任何基线检查报告")
        return None
        
    # 按修改时间排序，返回最新的报告
    latest_report = max(baseline_reports, key=lambda x: x[1])
    logger.info(f"找到最新的基线检查报告: {latest_report[0]}")
    return latest_report[0]

def parse_baseline_report(report_path: str) -> Dict[str, Any]:
    """解析基线检查报告，提取设备信息
    
    Args:
        report_path (str): 基线检查报告路径
        
    Returns:
        Dict[str, Any]: 解析后的报告数据
    """
    # 首先尝试查找对应的JSON文件
    json_path = report_path.replace('.html', '.json')
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    # 如果没有JSON文件，从HTML中提取信息
    try:
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取报告生成时间
        timestamp_match = re.search(r'生成时间:\s*([0-9\-:\s]+)', content)
        timestamp = timestamp_match.group(1) if timestamp_match else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 提取设备信息
        devices = []
        # 查找所有设备div块
        device_divs = re.split(r'(<div class="device"[^>]*id="[^"]+">)', content)
        # 重新组合设备div块
        device_blocks = []
        for i in range(1, len(device_divs), 2):
            if i + 1 < len(device_divs):
                device_blocks.append(device_divs[i] + device_divs[i+1])
        
        for device_content in device_blocks:
            # 提取设备ID（IP地址格式）
            device_id_match = re.search(r'id="([^"]+)"', device_content)
            if device_id_match:
                device_id = device_id_match.group(1)
                device_name = device_id.replace('-', '.')
                
                # 统计合规和不合规项
                compliant_count = len(re.findall(r'class="compliant"', device_content))
                non_compliant_count = len(re.findall(r'class="non-compliant"', device_content))
                total_checks = compliant_count + non_compliant_count
                
                devices.append({
                    'name': device_name,
                    'total_checks': total_checks,
                    'compliant_checks': compliant_count,
                    'non_compliant_checks': non_compliant_count
                })
        
        logger.info(f"从HTML报告中成功解析出 {len(devices)} 台设备信息")
        return {
            'timestamp': timestamp,
            'devices': devices
        }
    except Exception as e:
        logger.error(f"解析HTML报告失败: {str(e)}")
        # 如果解析失败，返回默认数据
        logger.warning("HTML报告解析失败，使用默认数据")
        return {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'devices': []
        }

def load_summary_template() -> Optional[str]:
    """加载汇总报告模板
    
    Returns:
        str: 模板内容，如果加载失败则返回None
    """
    template_path = 'templates/html/summary_report.html'
    if not os.path.exists(template_path):
        logger.error(f"汇总报告模板文件不存在: {template_path}")
        return None
        
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"加载汇总报告模板失败: {str(e)}")
        return None

def generate_summary_report_from_data(report_data: Dict[str, Any], detailed_report_filename: str) -> Optional[str]:
    """根据报告数据生成汇总报告
    
    Args:
        report_data (Dict[str, Any]): 基线检查报告数据
        detailed_report_filename (str): 详细报告文件名
        
    Returns:
        str: 生成的汇总报告路径，如果生成失败则返回None
    """
    # 加载模板
    template_content = load_summary_template()
    if not template_content:
        return None
        
    # 准备汇总报告数据
    summary_data = {
        'timestamp': report_data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        'devices': report_data.get('devices', []),
        'compliant_devices_count': 0,
        'non_compliant_devices_count': 0,
        'report_filename': detailed_report_filename
    }
    
    # 计算合规和不合规设备数量
    devices = summary_data['devices']
    compliant_count = 0
    non_compliant_count = 0
    
    for device in devices:
        # 根据设备是否包含不合规项来判断设备状态
        non_compliant_items = device.get('non_compliant_checks', 0)
        if non_compliant_items == 0:
            compliant_count += 1
        else:
            non_compliant_count += 1
    
    summary_data['compliant_devices_count'] = compliant_count
    summary_data['non_compliant_devices_count'] = non_compliant_count
    
    # 生成汇总报告
    try:
        template = Template(template_content)
        summary_html = template.render(**summary_data)
        
        # 保存汇总报告
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        summary_file = f"reports/summary_report_{timestamp}.html"
        
        os.makedirs('reports', exist_ok=True)
        with open(summary_file, 'w', encoding='utf-8-sig') as f:
            f.write(summary_html)
            
        logger.info(f"汇总报告已生成: {summary_file}")
        return summary_file
    except Exception as e:
        logger.error(f"生成汇总报告失败: {str(e)}")
        return None

def generate_summary_report() -> Optional[str]:
    """生成汇总报告的主函数
    
    Returns:
        str: 生成的汇总报告路径，如果生成失败则返回None
    """
    # 查找最新的基线检查报告
    latest_report = find_latest_baseline_report()
    if not latest_report:
        logger.error("无法找到最新的基线检查报告，无法生成汇总报告")
        return None
        
    # 解析基线检查报告
    report_data = parse_baseline_report(latest_report)
    
    # 从报告文件名提取详细报告文件名
    detailed_report_filename = os.path.basename(latest_report)
    
    # 生成汇总报告
    return generate_summary_report_from_data(report_data, detailed_report_filename)

if __name__ == '__main__':
    # 配置日志
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # 生成汇总报告
    summary_report_path = generate_summary_report()
    if summary_report_path:
        print(f"汇总报告已生成: {summary_report_path}")
    else:
        print("汇总报告生成失败")