import os
import re

def fix_summary_report(file_path):
    """修复汇总报告文件中的中文乱码"""
    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 定义乱码字符和对应的正确字符
    replacements = {
        '缃戠粶璁惧鍩虹嚎妫€鏌ユ眹鎬绘姤鍛?': '网络设备基线检查汇总报告',
        '鐢熸垚鏃堕棿': '生成时间',
        '妫€鏌ユ瑙?': '检查概览',
        '鎬昏澶囨暟': '总设备数',
        '鍚堣璁惧鏁?': '合规设备数',
        '涓嶅悎瑙勮澶囨暟': '不合规设备数',
        '璁惧璇︽儏': '设备详情',
        '璁惧': '设备',
        '妫€鏌ラ」鎬绘暟': '检查项总数',
        '鍚堣椤?': '合规项',
        '涓嶅悎瑙勯」': '不合规项',
        '鏌ョ湅璇︾粏鎶ュ憡': '查看详细报告',
        '杩斿洖鎶ュ憡椤甸潰鎸夐挳': '返回报告页面按钮',
        '杩斿洖鎶ュ憡椤甸潰': '返回报告页面',
        '鏉冮檺璁剧疆': '权限设置',
        '璁剧疆鏂囨湰鑷姩鎹㈣': '设置文本自动换行',
        '绗﹀悎': '符合',
        '涓嶇鍚?': '不符合',
        '閰嶇疆姝ｅ父': '配置正常',
        '瀛樺湪鏈叧闂帴鍙?': '存在未关闭接口',
        '鏃?': '无',
        '鏃犱慨澶嶅缓璁?': '无修复建议',
        '鏌ョ湅淇寤鸿': '查看修复建议',
        '鏌ョ湅淇鑴氭湰': '查看修复脚本',
        '鏄剧ず鎵€鏈変慨澶嶅缓璁甝': '显示所有修复建议',
        '闅愯棌鎵€鏈変慨澶嶅缓璁甝': '隐藏所有修复建议',
        '杩斿洖姹囨€绘姤鍛?': '返回汇总报告',
        '杩斿洖鎸夐挳鏍峰紡': '返回按钮样式'
    }
    
    # 替换乱码字符
    for garbled, correct in replacements.items():
        content = content.replace(garbled, correct)
    
    # 修复HTML标签问题
    content = re.sub(r'<title>([^<]+?)/title>', r'<title>\1</title>', content)
    content = re.sub(r'<h1>([^<]+?)/h1>', r'<h1>\1</h1>', content)
    content = re.sub(r'<h2>([^<]+?)/h2>', r'<h2>\1</h2>', content)
    content = re.sub(r'<div>([^<]+?)/div>', r'<div>\1</div>', content)
    
    # 写入修复后的内容
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"已修复文件: {file_path}")

def main():
    reports_dir = "reports"
    # 查找所有汇总报告文件
    for filename in os.listdir(reports_dir):
        if filename.startswith("summary_report") and filename.endswith(".html"):
            file_path = os.path.join(reports_dir, filename)
            try:
                fix_summary_report(file_path)
            except Exception as e:
                print(f"修复文件 {file_path} 时出错: {e}")

if __name__ == "__main__":
    main()