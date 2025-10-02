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
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'device', 'ssh_config.json')
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
    try:
        # 获取config/device目录下的所有文件
        config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'device')
        config_files = []
        
        if os.path.exists(config_dir):
            for filename in os.listdir(config_dir):
                file_path = os.path.join(config_dir, filename)
                if os.path.isfile(file_path):
                    # 获取文件的修改时间
                    mtime = os.path.getmtime(file_path)
                    # 获取文件大小
                    size = os.path.getsize(file_path)
                    config_files.append({
                        'filename': filename,
                        'mtime': mtime,
                        'size': size
                    })
        
        # 按文件名排序
        config_files.sort(key=lambda x: x['filename'])
        
        return render_template('config.html', config_files=config_files)
    except Exception as e:
        return f"读取配置文件列表时出错: {str(e)}", 500

@app.route('/config/device')
def list_device_configs():
    """列出设备配置文件"""
    return redirect(url_for('config'))

@app.route('/config/rule')
def list_rule_configs():
    """列出规则配置文件"""
    try:
        # 获取config/rule目录下的所有文件
        config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'rule')
        config_files = []
        
        if os.path.exists(config_dir):
            for filename in os.listdir(config_dir):
                file_path = os.path.join(config_dir, filename)
                if os.path.isfile(file_path):
                    # 获取文件的修改时间
                    mtime = os.path.getmtime(file_path)
                    # 获取文件大小
                    size = os.path.getsize(file_path)
                    config_files.append({
                        'filename': filename,
                        'mtime': mtime,
                        'size': size
                    })
        
        # 按文件名排序
        config_files.sort(key=lambda x: x['filename'])
        
        return jsonify({'status': 'success', 'config_files': config_files})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'读取规则配置文件列表时出错: {str(e)}'}), 500

@app.route('/config/itsm')
def list_system_configs():
    """列出系统配置文件"""
    try:
        # 获取config/itsm目录下的所有文件
        config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'itsm')
        config_files = []
        
        if os.path.exists(config_dir):
            for filename in os.listdir(config_dir):
                file_path = os.path.join(config_dir, filename)
                if os.path.isfile(file_path):
                    # 获取文件的修改时间
                    mtime = os.path.getmtime(file_path)
                    # 获取文件大小
                    size = os.path.getsize(file_path)
                    config_files.append({
                        'filename': filename,
                        'mtime': mtime,
                        'size': size
                    })
        
        # 按文件名排序
        config_files.sort(key=lambda x: x['filename'])
        
        return jsonify({'status': 'success', 'config_files': config_files})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'读取系统配置文件列表时出错: {str(e)}'}), 500

@app.route('/config/view_rule/<path:filename>')
def view_rule_config(filename):
    """查看规则配置文件"""
    try:
        # 构建文件路径
        config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'rule')
        file_path = os.path.join(config_dir, filename)
        
        # 安全检查：确保文件在config/rule目录中
        if not os.path.abspath(file_path).startswith(os.path.abspath(config_dir)):
            return "文件访问被拒绝", 403
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return "文件未找到", 404
            
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 确定文件类型
        if filename.endswith('.json'):
            file_type = 'JSON'
        elif filename.endswith('.yaml') or filename.endswith('.yml'):
            file_type = 'YAML'
        else:
            file_type = 'TEXT'
            
        # 准备传递给模板的数据
        config_data = {
            'name': filename,
            'type': file_type,
            'content': content
        }
        
        return render_template('config_view.html', config_data=config_data)
    except Exception as e:
        config_data = {
            'name': filename,
            'error': f'读取配置文件时出错: {str(e)}'
        }
        return render_template('config_view.html', config_data=config_data)

@app.route('/config/view_itsm/<path:filename>')
def view_system_config(filename):
    """查看系统配置文件"""
    try:
        # 构建文件路径
        config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'itsm')
        file_path = os.path.join(config_dir, filename)
        
        # 安全检查：确保文件在config/itsm目录中
        if not os.path.abspath(file_path).startswith(os.path.abspath(config_dir)):
            return "文件访问被拒绝", 403
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return "文件未找到", 404
            
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 确定文件类型
        if filename.endswith('.json'):
            file_type = 'JSON'
        elif filename.endswith('.yaml') or filename.endswith('.yml'):
            file_type = 'YAML'
        else:
            file_type = 'TEXT'
            
        # 准备传递给模板的数据
        config_data = {
            'name': filename,
            'type': file_type,
            'content': content
        }
        
        return render_template('config_view.html', config_data=config_data)
    except Exception as e:
        config_data = {
            'name': filename,
            'error': f'读取配置文件时出错: {str(e)}'
        }
        return render_template('config_view.html', config_data=config_data)

@app.route('/config/edit_rule/<path:filename>', methods=['GET', 'POST'])
def edit_rule_config(filename):
    """编辑规则配置文件"""
    config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'rule')
    file_path = os.path.join(config_dir, filename)
    
    if request.method == 'POST':
        try:
            content = request.form.get('content', '')
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return json.dumps({"success": True, "message": "文件保存成功"}), 200, {'ContentType':'application/json'}
        except Exception as e:
            return json.dumps({"success": False, "message": f"保存文件时出错: {str(e)}"}), 500, {'ContentType':'application/json'}
    else:
        try:
            # 确保文件存在且在config目录中
            if not os.path.exists(file_path) or not os.path.abspath(file_path).startswith(os.path.abspath(config_dir)):
                return "文件未找到", 404
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 确定文件类型
            if filename.endswith('.json'):
                file_type = 'JSON'
            elif filename.endswith('.yaml') or filename.endswith('.yml'):
                file_type = 'YAML'
            else:
                file_type = 'TEXT'
                
            return render_template('config_edit.html',
                                   filename=filename,
                                   content=content,
                                   file_type=file_type)
        except Exception as e:
            return f"读取文件时出错: {str(e)}", 500

@app.route('/config/edit_itsm/<path:filename>', methods=['GET', 'POST'])
def edit_system_config(filename):
    """编辑系统配置文件"""
    config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'itsm')
    file_path = os.path.join(config_dir, filename)
    
    if request.method == 'POST':
        try:
            content = request.form.get('content', '')
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return json.dumps({"success": True, "message": "文件保存成功"}), 200, {'ContentType':'application/json'}
        except Exception as e:
            return json.dumps({"success": False, "message": f"保存文件时出错: {str(e)}"}), 500, {'ContentType':'application/json'}
    else:
        try:
            # 确保文件存在且在config目录中
            if not os.path.exists(file_path) or not os.path.abspath(file_path).startswith(os.path.abspath(config_dir)):
                return "文件未找到", 404
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 确定文件类型
            if filename.endswith('.json'):
                file_type = 'JSON'
            elif filename.endswith('.yaml') or filename.endswith('.yml'):
                file_type = 'YAML'
            else:
                file_type = 'TEXT'
                
            return render_template('config_edit.html',
                                   filename=filename,
                                   content=content,
                                   file_type=file_type)
        except Exception as e:
            return f"读取文件时出错: {str(e)}", 500

@app.route('/config/delete_rule/<path:filename>', methods=['POST'])
def delete_rule_config(filename):
    """删除规则配置文件"""
    try:
        config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'rule')
        file_path = os.path.join(config_dir, filename)
        
        # 安全检查：确保文件在config/rule目录中
        if not os.path.abspath(file_path).startswith(os.path.abspath(config_dir)):
            return jsonify({'status': 'error', 'message': '文件访问被拒绝'}), 403
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return jsonify({'status': 'error', 'message': '文件未找到'}), 404
            
        # 删除文件
        os.remove(file_path)
        return jsonify({'status': 'success', 'message': f'文件 {filename} 已成功删除'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'删除文件时出错: {str(e)}'}), 500

@app.route('/config/delete_itsm/<path:filename>', methods=['POST'])
def delete_system_config(filename):
    """删除系统配置文件"""
    try:
        config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'itsm')
        file_path = os.path.join(config_dir, filename)
        
        # 安全检查：确保文件在config/itsm目录中
        if not os.path.abspath(file_path).startswith(os.path.abspath(config_dir)):
            return jsonify({'status': 'error', 'message': '文件访问被拒绝'}), 403
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return jsonify({'status': 'error', 'message': '文件未找到'}), 404
            
        # 删除文件
        os.remove(file_path)
        return jsonify({'status': 'success', 'message': f'文件 {filename} 已成功删除'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'删除文件时出错: {str(e)}'}), 500

@app.route('/config/backup_rule/<path:filename>', methods=['POST'])
def backup_rule_config(filename):
    """备份规则配置文件"""
    try:
        config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'rule')
        file_path = os.path.join(config_dir, filename)
        
        # 安全检查：确保文件在config/rule目录中
        if not os.path.abspath(file_path).startswith(os.path.abspath(config_dir)):
            return jsonify({'status': 'error', 'message': '文件访问被拒绝'}), 403
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return jsonify({'status': 'error', 'message': '文件未找到'}), 404
            
        # 创建备份文件名
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"{filename}.bak_{timestamp}"
        backup_path = os.path.join(config_dir, backup_filename)
        
        # 复制文件作为备份
        import shutil
        shutil.copy2(file_path, backup_path)
        
        return jsonify({'status': 'success', 'message': f'文件 {filename} 已成功备份为 {backup_filename}'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'备份文件时出错: {str(e)}'}), 500

@app.route('/config/backup_itsm/<path:filename>', methods=['POST'])
def backup_system_config(filename):
    """备份系统配置文件"""
    try:
        config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'itsm')
        file_path = os.path.join(config_dir, filename)
        
        # 安全检查：确保文件在config/itsm目录中
        if not os.path.abspath(file_path).startswith(os.path.abspath(config_dir)):
            return jsonify({'status': 'error', 'message': '文件访问被拒绝'}), 403
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return jsonify({'status': 'error', 'message': '文件未找到'}), 404
            
        # 创建备份文件名
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"{filename}.bak_{timestamp}"
        backup_path = os.path.join(config_dir, backup_filename)
        
        # 复制文件作为备份
        import shutil
        shutil.copy2(file_path, backup_path)
        
        return jsonify({'status': 'success', 'message': f'文件 {filename} 已成功备份为 {backup_filename}'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'备份文件时出错: {str(e)}'}), 500

@app.route('/config/restore_rule/<path:filename>', methods=['POST'])
def restore_rule_config(filename):
    """恢复规则配置文件（从备份）"""
    config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'rule')
    file_path = os.path.join(config_dir, filename)
    
    # 安全检查：确保文件在config/rule目录中
    if not os.path.abspath(file_path).startswith(os.path.abspath(config_dir)):
        return jsonify({'status': 'error', 'message': '无效的文件路径'}), 400
    
    # 查找最新的备份文件
    backup_prefix = f"{filename}.bak_"
    latest_backup = None
    latest_time = 0
    
    if os.path.exists(config_dir):
        for file in os.listdir(config_dir):
            if file.startswith(backup_prefix):
                backup_time = os.path.getmtime(os.path.join(config_dir, file))
                if backup_time > latest_time:
                    latest_time = backup_time
                    latest_backup = file
    
    if latest_backup:
        backup_path = os.path.join(config_dir, latest_backup)
        try:
            # 复制备份文件覆盖原文件
            import shutil
            shutil.copy2(backup_path, file_path)
            return jsonify({'status': 'success', 'message': f'配置文件 {filename} 已从备份恢复'})
        except Exception as e:
            return jsonify({'status': 'error', 'message': f'恢复配置文件时出错: {str(e)}'}), 500
    else:
        return jsonify({'status': 'error', 'message': '未找到备份文件'}), 404

@app.route('/config/restore_itsm/<path:filename>', methods=['POST'])
def restore_system_config(filename):
    """恢复系统配置文件（从备份）"""
    config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'itsm')
    file_path = os.path.join(config_dir, filename)
    
    # 安全检查：确保文件在config/itsm目录中
    if not os.path.abspath(file_path).startswith(os.path.abspath(config_dir)):
        return jsonify({'status': 'error', 'message': '无效的文件路径'}), 400
    
    # 查找最新的备份文件
    backup_prefix = f"{filename}.bak_"
    latest_backup = None
    latest_time = 0
    
    if os.path.exists(config_dir):
        for file in os.listdir(config_dir):
            if file.startswith(backup_prefix):
                backup_time = os.path.getmtime(os.path.join(config_dir, file))
                if backup_time > latest_time:
                    latest_time = backup_time
                    latest_backup = file
    
    if latest_backup:
        backup_path = os.path.join(config_dir, latest_backup)
        try:
            # 复制备份文件覆盖原文件
            import shutil
            shutil.copy2(backup_path, file_path)
            return jsonify({'status': 'success', 'message': f'配置文件 {filename} 已从备份恢复'})
        except Exception as e:
            return jsonify({'status': 'error', 'message': f'恢复配置文件时出错: {str(e)}'}), 500
    else:
        return jsonify({'status': 'error', 'message': '未找到备份文件'}), 404

@app.route('/config/view/<path:filename>')
def view_config_file(filename):
    """查看指定的配置文件"""
    try:
        # 构建文件路径
        config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'device')
        file_path = os.path.join(config_dir, filename)
        
        # 安全检查：确保文件在config/device目录中
        if not os.path.abspath(file_path).startswith(os.path.abspath(config_dir)):
            return "文件访问被拒绝", 403
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return "文件未找到", 404
            
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 确定文件类型
        if filename.endswith('.json'):
            file_type = 'JSON'
        elif filename.endswith('.yaml') or filename.endswith('.yml'):
            file_type = 'YAML'
        else:
            file_type = 'TEXT'
            
        # 准备传递给模板的数据
        config_data = {
            'name': filename,
            'type': file_type,
            'content': content
        }
        
        return render_template('config_view.html', config_data=config_data)
    except Exception as e:
        config_data = {
            'name': filename,
            'error': f'读取配置文件时出错: {str(e)}'
        }
        return render_template('config_view.html', config_data=config_data)

@app.route('/config/edit/<path:filename>', methods=['GET', 'POST'])
def edit_config(filename):
    """编辑配置文件"""
    config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'device')
    file_path = os.path.join(config_dir, filename)
    
    if request.method == 'POST':
        try:
            content = request.form.get('content', '')
            # 保持文件末尾的换行符格式
            if content and not content.endswith('\n'):
                # 检查原文件是否以换行符结尾
                original_content = ""
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        original_content = f.read()
                # 如果原文件以换行符结尾，则保持这个习惯
                if original_content.endswith('\n') or original_content.endswith('\r\n'):
                    content += '\n'
            
            with open(file_path, 'w', encoding='utf-8', newline='') as f:
                f.write(content)
            return json.dumps({"success": True, "message": "文件保存成功"}), 200, {'ContentType':'application/json'}
        except Exception as e:
            return json.dumps({"success": False, "message": f"保存文件时出错: {str(e)}"}), 500, {'ContentType':'application/json'}
    else:
        try:
            # 确保文件存在且在config目录中
            if not os.path.exists(file_path) or not os.path.abspath(file_path).startswith(os.path.abspath(config_dir)):
                return "文件未找到", 404
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 确定文件类型
            if filename.endswith('.json'):
                file_type = 'JSON'
            elif filename.endswith('.yaml') or filename.endswith('.yml'):
                file_type = 'YAML'
            else:
                file_type = 'TEXT'
                
            return render_template('config_edit.html',
                                   filename=filename,
                                   content=content,
                                   file_type=file_type)
        except Exception as e:
            return f"读取文件时出错: {str(e)}", 500

@app.route('/config/delete/<path:filename>', methods=['POST'])
def delete_config(filename):
    """删除配置文件"""
    try:
        config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'device')
        file_path = os.path.join(config_dir, filename)
        
        # 安全检查：确保文件在config/device目录中
        if not os.path.abspath(file_path).startswith(os.path.abspath(config_dir)):
            return jsonify({'status': 'error', 'message': '文件访问被拒绝'}), 403
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return jsonify({'status': 'error', 'message': '文件未找到'}), 404
            
        # 删除文件
        os.remove(file_path)
        return jsonify({'status': 'success', 'message': f'文件 {filename} 已成功删除'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'删除文件时出错: {str(e)}'}), 500

@app.route('/config/backup/<path:filename>', methods=['POST'])
def backup_config(filename):
    """备份配置文件"""
    try:
        config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'device')
        file_path = os.path.join(config_dir, filename)
        
        # 安全检查：确保文件在config/device目录中
        if not os.path.abspath(file_path).startswith(os.path.abspath(config_dir)):
            return jsonify({'status': 'error', 'message': '文件访问被拒绝'}), 403
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return jsonify({'status': 'error', 'message': '文件未找到'}), 404
            
        # 创建备份文件名
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"{filename}.bak_{timestamp}"
        backup_path = os.path.join(config_dir, backup_filename)
        
        # 复制文件作为备份
        import shutil
        shutil.copy2(file_path, backup_path)
        
        return jsonify({'status': 'success', 'message': f'文件 {filename} 已成功备份为 {backup_filename}'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'备份文件时出错: {str(e)}'}), 500

@app.route('/config/restore/<path:filename>', methods=['POST'])
def restore_config(filename):
    """恢复配置文件（从备份）"""
    config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'device')
    file_path = os.path.join(config_dir, filename)
    
    # 安全检查：确保文件在config/device目录中
    if not os.path.abspath(file_path).startswith(os.path.abspath(config_dir)):
        return jsonify({'status': 'error', 'message': '无效的文件路径'}), 400
    
    # 查找最新的备份文件
    backup_prefix = f"{filename}.bak_"
    latest_backup = None
    latest_time = 0
    
    if os.path.exists(config_dir):
        for file in os.listdir(config_dir):
            if file.startswith(backup_prefix):
                backup_time = os.path.getmtime(os.path.join(config_dir, file))
                if backup_time > latest_time:
                    latest_time = backup_time
                    latest_backup = file
    
    if latest_backup:
        backup_path = os.path.join(config_dir, latest_backup)
        try:
            # 复制备份文件覆盖原文件
            import shutil
            shutil.copy2(backup_path, file_path)
            return jsonify({'status': 'success', 'message': f'配置文件 {filename} 已从备份恢复'})
        except Exception as e:
            return jsonify({'status': 'error', 'message': f'恢复配置文件时出错: {str(e)}'}), 500
    else:
        return jsonify({'status': 'error', 'message': '未找到备份文件'}), 404

@app.route('/test_css')
def test_css():
    """测试CSS样式"""
    return render_template('test_css.html')

@app.route('/test_table')
def test_table():
    """测试表格样式"""
    return render_template('test_table.html')

@app.route('/debug_table')
def debug_table():
    """调试表格样式"""
    return render_template('debug_table.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)