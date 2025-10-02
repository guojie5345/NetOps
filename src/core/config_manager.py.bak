import json
import os

class ConfigManager:
    """配置管理类"""
    def __init__(self, config_path=None, ssh_config_path=None, api_config_path=None, scenario_config_path=None):
        """初始化配置管理器

        Args:
            config_path: 通用配置文件路径（可选）
            ssh_config_path: SSH配置文件路径（可选）
            api_config_path: API配置文件路径（可选）
            scenario_config_path: 场景配置文件路径（可选）
        """
        self.config_path = config_path
        self.ssh_config_path = ssh_config_path
        self.api_config_path = api_config_path
        self.scenario_config_path = scenario_config_path
        self.config = {}

    def load_config(self):
        """加载配置文件

        Returns:
            dict: 配置字典
        """
        # 加载通用配置文件（如果提供）
        if self.config_path and os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            # 如果没有提供通用配置文件或文件不存在，创建空配置
            self.config = {}
        
        # 加载SSH配置文件（如果提供）
        if self.ssh_config_path and os.path.exists(self.ssh_config_path):
            with open(self.ssh_config_path, 'r', encoding='utf-8') as f:
                ssh_config = json.load(f)
                self.config.update(ssh_config)
        
        # 加载API配置文件（如果提供）
        if self.api_config_path and os.path.exists(self.api_config_path):
            with open(self.api_config_path, 'r', encoding='utf-8') as f:
                api_config = json.load(f)
                self.config.update(api_config)

        # 如果存在场景配置文件，则加载并合并到主配置中
        if self.scenario_config_path and os.path.exists(self.scenario_config_path):
            with open(self.scenario_config_path, 'r', encoding='utf-8') as f:
                scenario_config = json.load(f)
                self.config['scenario_config'] = scenario_config

        return self.config

    def save_config(self, config=None):
        """保存配置文件

        Args:
            config: 配置字典，如果为None则保存当前配置
        """
        if config is not None:
            self.config = config

        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

        return True
        
    def save_ssh_config(self, ssh_config=None):
        """保存SSH配置文件

        Args:
            ssh_config: SSH配置字典，如果为None则保存当前配置中的SSH部分
        """
        if not self.ssh_config_path:
            raise ValueError("SSH配置文件路径未设置")
            
        if ssh_config is not None:
            # 确保配置中只包含SSH相关配置
            if 'ssh_devices' in ssh_config:
                config_to_save = {'ssh_devices': ssh_config['ssh_devices']}
            else:
                config_to_save = {'ssh_devices': []}
        else:
            # 从当前配置中提取SSH相关配置
            config_to_save = {'ssh_devices': self.config.get('ssh_devices', [])}

        with open(self.ssh_config_path, 'w', encoding='utf-8') as f:
            json.dump(config_to_save, f, ensure_ascii=False, indent=2)

        return True
        
    def save_api_config(self, api_config=None):
        """保存API配置文件

        Args:
            api_config: API配置字典，如果为None则保存当前配置中的API部分
        """
        if not self.api_config_path:
            raise ValueError("API配置文件路径未设置")
            
        if api_config is not None:
            # 确保配置中只包含API相关配置
            if 'api_endpoints' in api_config:
                config_to_save = {'api_endpoints': api_config['api_endpoints']}
            else:
                config_to_save = {'api_endpoints': []}
        else:
            # 从当前配置中提取API相关配置
            config_to_save = {'api_endpoints': self.config.get('api_endpoints', [])}

        with open(self.api_config_path, 'w', encoding='utf-8') as f:
            json.dump(config_to_save, f, ensure_ascii=False, indent=2)

        return True