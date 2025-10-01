#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化运维工具Web应用程序
"""

import os
import sys
import json
from flask import Flask, render_template, request, redirect, url_for, send_from_directory

# 将项目根目录添加到Python路径中
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入基线检查模块
try:
    from src.modules.baseline.check_baseline import BaselineChecker
    from src.modules.baseline.generate_summary_report import generate_summary_report_from_data
except ImportError as e:
    print(f"导入模块时出错: {e}")
    BaselineChecker = None
    generate_summary_report_from_data = None

app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')

# 配置
app.config['SECRET_KEY'] = 'your-secret_key_here'
# 使用项目根目录下的reports文件夹，与check_baseline.py保持一致
app.config['REPORTS_DIR'] = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'reports')

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/devices')
def devices():
    """设备管理页面"""
    # 这里应该从配置文件或数据库中读取设备信息
    # 为了简化，我们使用硬编码的数据
    device_list = [
        {'ip': '192.168.80.21', 'name': 'Device 1'},
        {'ip': '192.168.80.22', 'name': 'Device 2'}
    ]
    return render_template('devices.html', devices=device_list)

import json
import threading

# 全局变量用于跟踪检查状态
check_status = {
    'is_running': False,
    'progress': 0,
    'message': ''
}

def run_baseline_check(devices):
    """在后台线程中运行基线检查"""
    global check_status
    try:
        check_status['is_running'] = True
        check_status['progress'] = 0
        check_status['message'] = '正在初始化检查...'
        
        # 模拟进度更新
        check_status['progress'] = 10
        check_status['message'] = '正在连接设备...'
        
        # 执行基线检查
        checker = BaselineChecker()
        checker.check_baseline(devices)
        
        check_status['progress'] = 100
        check_status['message'] = '检查完成'
        check_status['completed'] = True
    except Exception as e:
        check_status['message'] = f'执行基线检查时出错: {str(e)}'
        check_status['completed'] = False
    finally:
        check_status['is_running'] = False

@app.route('/baseline_check', methods=['GET'])
def baseline_check():
    """基线检查页面"""
    global check_status
    
    # GET请求重置检查状态
    check_status = {
        'is_running': False,
        'progress': 0,
        'message': '',
        'completed': False
    }
    
    return render_template('baseline_check.html')

def load_ssh_config():
    """从配置文件加载SSH设备信息"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'ssh_config.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            # 转换设备类型以匹配基线检查器的期望
            devices = []
            for device in config.get('ssh_devices', []):
                # 复制设备信息
                new_device = device.copy()
                # 如果设备类型是cisco_ios，转换为hillstone（根据之前的代码）
                if new_device.get('device_type') == 'cisco_ios':
                    new_device['device_type'] = 'hillstone'
                devices.append(new_device)
            return devices
    except FileNotFoundError:
        print(f"配置文件未找到: {config_path}")
        return []
    except Exception as e:
        print(f"读取配置文件时出错: {e}")
        return []

@app.route('/baseline_check/start', methods=['POST'])
def start_baseline_check():
    """启动基线检查"""
    global check_status
    
    # 检查是否已导入必要的模块
    if BaselineChecker is None:
        return json.dumps({'status': 'error', 'message': '错误：未能导入基线检查模块'}), 500, {'ContentType':'application/json'}
        
    # 如果检查已经在运行，返回错误
    if check_status['is_running']:
        return json.dumps({'status': 'error', 'message': '检查已在运行中'}), 400, {'ContentType':'application/json'}
    
    try:
        # 从配置文件获取设备信息
        devices = load_ssh_config()
        
        if not devices:
            return json.dumps({'status': 'error', 'message': '未找到设备配置信息'}), 500, {'ContentType':'application/json'}
        
        # 在后台线程中启动检查
        thread = threading.Thread(target=run_baseline_check, args=(devices,))
        thread.start()
        
        return json.dumps({'status': 'started'}), 200, {'ContentType':'application/json'}
    except Exception as e:
        return json.dumps({'status': 'error', 'message': f'启动基线检查时出错: {str(e)}'}), 500, {'ContentType':'application/json'}

@app.route('/baseline_check/status', methods=['GET'])
def baseline_check_status():
    """获取基线检查状态"""
    global check_status
    
    # 返回检查状态
    response_data = {
        'status': 'running' if check_status['is_running'] else ('completed' if check_status.get('completed', False) else 'idle'),
        'progress': check_status['progress'],
        'message': check_status['message']
    }
    
    return json.dumps(response_data), 200, {'ContentType':'application/json'}

@app.route('/reports')
def reports():
    """报告查看页面"""
    # 获取所有报告文件
    reports_dir = app.config['REPORTS_DIR']
    html_reports = []
    summary_reports = []
    excel_reports = []
    
    if os.path.exists(reports_dir):
        try:
            for filename in os.listdir(reports_dir):
                if filename.endswith('.html') and filename.startswith('baseline_report_'):
                    html_reports.append(filename)
                elif filename.endswith('.html') and filename.startswith('summary_report_'):
                    summary_reports.append(filename)
                elif filename.endswith('.xlsx') and filename.startswith('baseline_report_'):
                    excel_reports.append(filename)
            
            # 按修改时间排序
            html_reports.sort(key=lambda x: os.path.getmtime(os.path.join(reports_dir, x)), reverse=True)
            summary_reports.sort(key=lambda x: os.path.getmtime(os.path.join(reports_dir, x)), reverse=True)
            excel_reports.sort(key=lambda x: os.path.getmtime(os.path.join(reports_dir, x)), reverse=True)
        except Exception as e:
            print(f"读取报告目录时出错: {e}")
    
    return render_template('reports.html', html_reports=html_reports, summary_reports=summary_reports, excel_reports=excel_reports)

@app.route('/reports/<path:filename>')  # 使用path转换器以支持包含点的文件名
def report_file(filename):
    """提供报告文件下载或查看"""
    try:
        return send_from_directory(app.config['REPORTS_DIR'], filename)
    except Exception as e:
        return f"无法找到文件: {filename}", 404

@app.route('/config')
def config():
    """配置管理页面"""
    return render_template('config.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)