"""日志配置模块

本文件负责配置日志系统，提供统一的日志记录功能。
"""

import logging
import os
from logging.handlers import RotatingFileHandler

# 确保日志目录存在
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(
            os.path.join(log_dir, "ai-engine.log"),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        ),
        logging.StreamHandler()
    ]
)

# 创建日志记录器
def get_logger(name):
    """获取日志记录器
    
    Args:
        name: 日志记录器名称
    
    Returns:
        日志记录器对象
    """
    return logging.getLogger(name)
