"""测试日志模块

本文件测试logger.py模块的功能。
"""

import pytest
from utils.logger import get_logger


def test_get_logger():
    """测试获取日志记录器"""
    logger = get_logger(__name__)
    assert logger is not None
    assert logger.name == __name__
    
    # 测试日志级别
    assert logger.level <= 20  # INFO级别
    
    # 测试日志输出
    try:
        logger.info("测试日志信息")
        logger.error("测试错误信息")
    except Exception as e:
        pytest.fail(f"日志记录失败: {e}")
