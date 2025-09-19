import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logger():
    """设置日志系统"""
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, 'itsm_automation.log')

    # 配置日志格式
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'

    # 设置根日志器
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # 检查是否已存在处理器，避免重复添加
    if logger.handlers:
        return logger

    # 控制台日志处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format, date_format))
    logger.addHandler(console_handler)

    # 文件日志处理器
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=1024 * 1024 * 10,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(logging.Formatter(log_format, date_format))
    logger.addHandler(file_handler)

    return logger
