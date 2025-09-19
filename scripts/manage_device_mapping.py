#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
设备映射配置管理脚本
提供简单的命令行界面来管理设备映射配置
"""

import json
import os

# 配置文件路径
CONFIG_PATH = os.path.join('e:/Development/Python/NetOps/src/config', 'device_mapping_config.json')

def load_config():
    """加载配置文件"""
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"配置文件未找到: {CONFIG_PATH}")
        return None
    except json.JSONDecodeError as e:
        print(f"配置文件格式错误: {e}")
        return None

def save_config(config):
    """保存配置文件"""
    try:
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        print("配置已保存")
        return True
    except Exception as e:
        print(f"保存配置文件时出错: {e}")
        return False

def show_config():
    """显示当前配置"""
    config = load_config()
    if config is None:
        return
    
    print("\n=== 当前设备映射配置 ===")
    print("\n模板匹配规则 (template_mapping):")
    for device_type, keywords in config.get('template_mapping', {}).items():
        print(f"  {device_type}: {keywords}")
    
    print("\n主机名匹配规则 (hostname_mapping):")
    for device_type, keywords in config.get('hostname_mapping', {}).items():
        print(f"  {device_type}: {keywords}")
    
    print("\n网络设备类型 (network_device_types):")
    for device_type in config.get('network_device_types', []):
        print(f"  - {device_type}")

def add_template_mapping():
    """添加模板匹配规则"""
    config = load_config()
    if config is None:
        return
    
    device_type = input("请输入设备类型 (如 cisco_ios): ").strip()
    keywords_input = input("请输入关键词 (用逗号分隔): ").strip()
    keywords = [kw.strip() for kw in keywords_input.split(',') if kw.strip()]
    
    if not device_type or not keywords:
        print("设备类型和关键词不能为空")
        return
    
    if 'template_mapping' not in config:
        config['template_mapping'] = {}
    
    # 检查是否已存在该设备类型的规则
    if device_type in config['template_mapping']:
        # 询问用户是覆盖还是合并
        print(f"设备类型 {device_type} 已存在以下规则: {config['template_mapping'][device_type]}")
        action = input("请选择操作 - (a)追加关键词, (r)替换规则, (c)取消: ").strip().lower()
        if action == 'r':
            # 替换规则
            config['template_mapping'][device_type] = keywords
            print(f"已替换模板匹配规则: {device_type} -> {keywords}")
        elif action == 'a':
            # 追加关键词（去重）
            existing_keywords = config['template_mapping'][device_type]
            new_keywords = list(set(existing_keywords + keywords))
            config['template_mapping'][device_type] = new_keywords
            print(f"已更新模板匹配规则: {device_type} -> {new_keywords}")
        else:
            print("操作已取消")
            return
    else:
        # 添加新规则
        config['template_mapping'][device_type] = keywords
        print(f"已添加模板匹配规则: {device_type} -> {keywords}")
    
    # 如果该设备类型不在网络设备类型列表中，询问是否添加
    if device_type not in config.get('network_device_types', []):
        add_to_network = input(f"是否将 {device_type} 添加到网络设备类型列表? (y/n): ").strip().lower()
        if add_to_network == 'y':
            if 'network_device_types' not in config:
                config['network_device_types'] = []
            config['network_device_types'].append(device_type)
            print(f"已将 {device_type} 添加到网络设备类型列表")
    
    save_config(config)

def add_hostname_mapping():
    """添加主机名匹配规则"""
    config = load_config()
    if config is None:
        return
    
    device_type = input("请输入设备类型 (如 cisco_ios): ").strip()
    keywords_input = input("请输入关键词 (用逗号分隔): ").strip()
    keywords = [kw.strip() for kw in keywords_input.split(',') if kw.strip()]
    
    if not device_type or not keywords:
        print("设备类型和关键词不能为空")
        return
    
    if 'hostname_mapping' not in config:
        config['hostname_mapping'] = {}
    
    # 检查是否已存在该设备类型的规则
    if device_type in config['hostname_mapping']:
        # 询问用户是覆盖还是合并
        print(f"设备类型 {device_type} 已存在以下规则: {config['hostname_mapping'][device_type]}")
        action = input("请选择操作 - (a)追加关键词, (r)替换规则, (c)取消: ").strip().lower()
        if action == 'r':
            # 替换规则
            config['hostname_mapping'][device_type] = keywords
            print(f"已替换主机名匹配规则: {device_type} -> {keywords}")
        elif action == 'a':
            # 追加关键词（去重）
            existing_keywords = config['hostname_mapping'][device_type]
            new_keywords = list(set(existing_keywords + keywords))
            config['hostname_mapping'][device_type] = new_keywords
            print(f"已更新主机名匹配规则: {device_type} -> {new_keywords}")
        else:
            print("操作已取消")
            return
    else:
        # 添加新规则
        config['hostname_mapping'][device_type] = keywords
        print(f"已添加主机名匹配规则: {device_type} -> {keywords}")
    save_config(config)

def add_network_device_type():
    """添加网络设备类型"""
    config = load_config()
    if config is None:
        return
    
    device_type = input("请输入设备类型: ").strip()
    
    if not device_type:
        print("设备类型不能为空")
        return
    
    if 'network_device_types' not in config:
        config['network_device_types'] = []
    
    if device_type in config['network_device_types']:
        print(f"设备类型 {device_type} 已存在于网络设备类型列表中")
        return
    
    config['network_device_types'].append(device_type)
    print(f"已将 {device_type} 添加到网络设备类型列表")
    save_config(config)

def remove_template_mapping():
    """删除模板匹配规则"""
    config = load_config()
    if config is None:
        return
    
    device_type = input("请输入要删除的设备类型: ").strip()
    
    if 'template_mapping' not in config or device_type not in config['template_mapping']:
        print(f"未找到设备类型 {device_type} 的模板匹配规则")
        return
    
    del config['template_mapping'][device_type]
    print(f"已删除 {device_type} 的模板匹配规则")
    save_config(config)

def remove_hostname_mapping():
    """删除主机名匹配规则"""
    config = load_config()
    if config is None:
        return
    
    device_type = input("请输入要删除的设备类型: ").strip()
    
    if 'hostname_mapping' not in config or device_type not in config['hostname_mapping']:
        print(f"未找到设备类型 {device_type} 的主机名匹配规则")
        return
    
    del config['hostname_mapping'][device_type]
    print(f"已删除 {device_type} 的主机名匹配规则")
    save_config(config)

def remove_network_device_type():
    """删除网络设备类型"""
    config = load_config()
    if config is None:
        return
    
    device_type = input("请输入要删除的设备类型: ").strip()
    
    if 'network_device_types' not in config or device_type not in config['network_device_types']:
        print(f"设备类型 {device_type} 不在网络设备类型列表中")
        return
    
    config['network_device_types'].remove(device_type)
    print(f"已从网络设备类型列表中删除 {device_type}")
    save_config(config)

def main():
    """主函数"""
    while True:
        print("\n=== 设备映射配置管理 ===")
        print("1. 显示当前配置")
        print("2. 添加模板匹配规则")
        print("3. 添加主机名匹配规则")
        print("4. 添加网络设备类型")
        print("5. 删除模板匹配规则")
        print("6. 删除主机名匹配规则")
        print("7. 删除网络设备类型")
        print("0. 退出")
        
        choice = input("\n请选择操作 (0-7): ").strip()
        
        if choice == '1':
            show_config()
        elif choice == '2':
            add_template_mapping()
        elif choice == '3':
            add_hostname_mapping()
        elif choice == '4':
            add_network_device_type()
        elif choice == '5':
            remove_template_mapping()
        elif choice == '6':
            remove_hostname_mapping()
        elif choice == '7':
            remove_network_device_type()
        elif choice == '0':
            print("退出程序")
            break
        else:
            print("无效选择，请重新输入")

if __name__ == "__main__":
    main()