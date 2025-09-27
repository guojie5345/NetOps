import logging
import os
from logging.handlers import RotatingFileHandler


# 全局变量存储根日志器和日志目录
_root_logger = None
_log_dir = None


def setup_logger(name=None):
    """
    设置日志系统，支持为不同模块创建独立的子logger
    
    Args:
        name (str): 模块名称，如果提供则创建子logger，否则创建根logger
        
    Returns:
        logging.Logger: 配置好的logger实例
    """
    global _root_logger, _log_dir
    
    # 设置日志目录
    if _log_dir is None:
        _log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
        if not os.path.exists(_log_dir):
            os.makedirs(_log_dir)
    
    # 如果提供了名称，则创建子logger
    if name:
        return logging.getLogger(name)
    
    # 创建根logger（只创建一次）
    if _root_logger is not None:
        return _root_logger
    
    # 配置日志格式
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # 设置根日志器
    _root_logger = logging.getLogger()
    _root_logger.setLevel(logging.INFO)
    
    # 清除现有的处理器，避免重复添加
    _root_logger.handlers.clear()
    
    # 控制台日志处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format, date_format))
    _root_logger.addHandler(console_handler)
    
    # 文件日志处理器（统一存储到logs目录）
    log_file = os.path.join(_log_dir, 'itsm_automation.log')
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=1024 * 1024 * 10,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(logging.Formatter(log_format, date_format))
    _root_logger.addHandler(file_handler)
    
    return _root_logger


def get_module_logger(module_name):
    """
    为特定模块获取独立的logger
    
    Args:
        module_name (str): 模块名称
        
    Returns:
        logging.Logger: 该模块的logger实例
    """
    # 确保根logger已设置
    if _root_logger is None:
        setup_logger()
    
    # 创建模块的子logger
    module_logger = logging.getLogger(module_name)
    module_logger.setLevel(logging.INFO)
    
    return module_logger
