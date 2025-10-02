#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化运维工具Web应用程序
"""

import os
import sys
import json
import datetime
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify

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

# 添加自定义过滤器来格式化日期时间
@app.template_filter('datetimeformat')
def datetimeformat(value, format='%Y-%m-%d %H:%M:%S'):
    """将时间戳格式化为指定格式的日期时间字符串"""
    if value is None:
        return ""
    return datetime.datetime.fromtimestamp(value).strftime(format)

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
        check_status['completed'] = False  # 确保开始时 completed 为 False
        
        # 初始化进度
        check_status['progress'] = 5
        check_status['message'] = '正在准备检查环境...'
        
        # 连接设备进度
        check_status['progress'] = 10
        check_status['message'] = '正在连接设备...'
        
        # 执行基线检查
        checker = BaselineChecker()
        
        # 更新进度 - 开始检查
        check_status['progress'] = 20
        check_status['message'] = f'开始检查 {len(devices)} 台设备...'
        
        # 执行检查
        checker.check_baseline(devices)
        
        # 更新进度到100%
        check_status['progress'] = 100
        check_status['message'] = '检查完成'
        check_status['completed'] = True
    except Exception as e:
        check_status['progress'] = 100  # 即使出错也将进度设为100%，以便用户能看到错误信息
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
            # 保持设备类型不变，基线检查器支持cisco_ios类型
            devices = []
            for device in config.get('ssh_devices', []):
                # 复制设备信息
                new_device = device.copy()
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
                file_path = os.path.join(reports_dir, filename)
                if os.path.isfile(file_path):  # 确保是文件而不是目录
                    # 获取文件的修改时间
                    mtime = os.path.getmtime(file_path)
                    report_info = {
                        'filename': filename,
                        'mtime': mtime
                    }
                    
                    if filename.endswith('.html') and filename.startswith('baseline_report_'):
                        html_reports.append(report_info)
                    elif filename.endswith('.html') and filename.startswith('summary_report_'):
                        summary_reports.append(report_info)
                    elif filename.endswith('.xlsx') and filename.startswith('baseline_report_'):
                        excel_reports.append(report_info)
            
            # 按修改时间排序
            html_reports.sort(key=lambda x: x['mtime'], reverse=True)
            summary_reports.sort(key=lambda x: x['mtime'], reverse=True)
            excel_reports.sort(key=lambda x: x['mtime'], reverse=True)
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

@app.route('/reports/delete/<path:filename>', methods=['POST'])
def delete_report(filename):
    """删除报告文件及其相关文件"""
    try:
        # 提取文件的时间戳部分（例如：20251002_155504）
        # 文件名格式为：summary_report_20251002_155504.html 或 baseline_report_20251002_155504.html 或 baseline_report_20251002_155504.xlsx
        import re
        timestamp_match = re.search(r'(\d{8}_\d{6})', filename)
        if not timestamp_match:
            return jsonify({'status': 'error', 'message': '无法识别文件时间戳'}), 400
        
        timestamp = timestamp_match.group(1)
        
        # 查找所有包含相同时戳的报告文件
        reports_dir = app.config['REPORTS_DIR']
        related_files = []
        
        if os.path.exists(reports_dir):
            for file in os.listdir(reports_dir):
                if timestamp in file and os.path.isfile(os.path.join(reports_dir, file)):
                    related_files.append(file)
        
        # 删除所有相关文件
        deleted_files = []
        error_files = []
        
        for file in related_files:
            file_path = os.path.join(reports_dir, file)
            # 确保文件存在且在报告目录中
            if os.path.exists(file_path) and os.path.isfile(file_path):
                # 检查文件是否在报告目录中，防止路径遍历攻击
                reports_dir_abs = os.path.abspath(reports_dir)
                file_path_abs = os.path.abspath(file_path)
                if file_path_abs.startswith(reports_dir_abs):
                    try:
                        os.remove(file_path)
                        deleted_files.append(file)
                    except Exception as e:
                        error_files.append(file)
                else:
                    error_files.append(file)
            else:
                error_files.append(file)
        
        if error_files:
            return jsonify({'status': 'error', 'message': f'部分文件删除失败: {", ".join(error_files)}'}), 500
        else:
            return jsonify({'status': 'success', 'message': f'已删除 {len(deleted_files)} 个相关文件', 'deleted_files': deleted_files})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'删除文件时出错: {str(e)}'}), 500

@app.route('/config')
def config():
    """配置管理页面"""
    return render_template('config.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)