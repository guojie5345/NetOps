import json
import os

class ConfigManager:
    """配置管理类"""
    def __init__(self, config_path, scenario_config_path=None):
        """初始化配置管理器

        Args:
            config_path: 配置文件路径
            scenario_config_path: 场景配置文件路径
        """
        self.config_path = config_path
        self.scenario_config_path = scenario_config_path
        self.config = {}

    def load_config(self):
        """加载配置文件

        Returns:
            dict: 配置字典
        """
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f'配置文件不存在: {self.config_path}')

        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
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