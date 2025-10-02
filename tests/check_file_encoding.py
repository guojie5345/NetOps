import chardet

# 检查文件编码
with open('templates/html/baseline_report.html', 'rb') as f:
    raw_data = f.read()
    encoding_info = chardet.detect(raw_data)
    print(f"文件编码: {encoding_info}")

# 尝试以正确编码读取文件
try:
    with open('templates/html/baseline_report.html', 'r', encoding=encoding_info['encoding']) as f:
        content = f.read()
        print("文件内容前100个字符:")
        print(content[:100])
except Exception as e:
    print(f"读取文件时出错: {e}")