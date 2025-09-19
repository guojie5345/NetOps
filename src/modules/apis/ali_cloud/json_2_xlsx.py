#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# @Project  :DevOps
# @FileName :json_2_xlsx.py
# @Time     :2025/7/14 15:58
# @Author   :George


import json
import pandas as pd


def convert_json_to_excel(input_file, output_file):
    """
    将JSON文件转换为Excel表格
    :param input_file: 输入的JSON文件路径
    :param output_file: 输出的Excel文件路径
    """
    try:
        # 读取并解析JSON文件（原有代码保留）
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 提取目标数据（原有代码保留）
        instances = data.get('Instances', {})
        instance_list = instances.get('Instance', [])

        # 验证数据格式（原有代码保留）
        if not isinstance(instance_list, list):
            raise ValueError("Instances.Instance 应为列表格式")

        # 展开嵌套数据（保持不变）
        df = pd.json_normalize(instance_list)

        # 关键修改：将点分隔的列名转换为多级表头（MultiIndex）
        # if any('.' in col for col in df.columns):
        #     # 将 "detail.name" 分割为 ("detail", "name") 元组，生成多级索引
        #     df.columns = pd.MultiIndex.from_tuples(
        #         [tuple(col.split('.')) if '.' in col else (col, '') for col in df.columns]
        #     )

        print(df.columns)

        # 导出到Excel（pandas 1.5.3支持MultiIndex+index=False）
        # 关键修改：显式指定xlsxwriter引擎，设置index=False
        df.to_excel(output_file, engine='xlsxwriter', header=True)
        print(f"转换成功! 已生成: {output_file}")
        print(f"共转换 {len(df)} 行数据, {len(df.columns)} 列数据")

    except Exception as e:
        print(f"转换失败: {str(e)}")
        # 这里可能会有局部变量 'df' 未定义的问题，可考虑移除或添加检查
        # df.to_excel(output_file, index=False)  # 临时测试用


if __name__ == "__main__":
    # 执行转换
    input_file = 'instances.json'
    output_file = 'output.xlsx'
    convert_json_to_excel(input_file, output_file)


# # 测试数据（替换原 input_file 路径）
# test_data = {
#     "Instances": {
#         "Instance": [
#             {"id": 1, "detail": {"name": "张三", "age": 25}},
#             {"id": 2, "detail": {"name": "李四", "age": 30}}
#         ]
#     }
# }
#
# # 临时写入测试文件
# with open("instances.json", "w", encoding="utf-8") as f:
#     json.dump(test_data, f)
#
# # # 执行转换（替换原 input_file 为 "test.json"）
# # convert_json_to_excel("instances.json", "test_output.xlsx")