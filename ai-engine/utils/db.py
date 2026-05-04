"""数据库连接模块

本文件实现数据库连接和基本操作，用于存储和读取对话历史。
"""

import mysql.connector
from mysql.connector import Error
from config.config import settings
from utils.logger import get_logger
from utils.exceptions import DBException

# 创建日志记录器
logger = get_logger(__name__)


def get_db_connection():
    """获取数据库连接
    
    Returns:
        mysql.connector.connection_cext.CMySQLConnection: 数据库连接对象
    """
    try:
        connection = mysql.connector.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            database=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        if connection.is_connected():
            logger.info(f"成功连接到数据库: {settings.DB_NAME}")
        return connection
    except Error as e:
        logger.error(f"数据库连接失败: {str(e)}")
        raise DBException(f"数据库连接失败: {str(e)}")


def execute_update(query, params=None, conn=None, cursor=None):
    """执行更新操作
    
    Args:
        query: SQL更新语句
        params: 查询参数
        conn: 数据库连接对象（可选）
        cursor: 游标对象（可选）
    
    Returns:
        int: 受影响的行数
    """
    local_conn = conn
    local_cursor = cursor
    try:
        if not local_conn:
            local_conn = get_db_connection()
        if not local_cursor:
            local_cursor = local_conn.cursor()
        local_cursor.execute(query, params or ())
        affected_rows = local_cursor.rowcount
        if not conn:
            local_conn.commit()
        return affected_rows
    except Error as e:
        logger.error(f"执行更新失败: {str(e)}")
        if local_conn and not conn:
            local_conn.rollback()
        raise DBException(f"执行更新失败: {str(e)}")
    finally:
        if not cursor and local_cursor:
            local_cursor.close()
        if not conn and local_conn:
            local_conn.close()


def execute_query(query, params=None, conn=None, cursor=None):
    """执行查询
    
    Args:
        query: SQL查询语句
        params: 查询参数
        conn: 数据库连接对象（可选）
        cursor: 游标对象（可选）
    
    Returns:
        list: 查询结果
    """
    local_conn = conn
    local_cursor = cursor
    try:
        if not local_conn:
            local_conn = get_db_connection()
        if not local_cursor:
            local_cursor = local_conn.cursor(dictionary=True)
        local_cursor.execute(query, params or ())
        result = local_cursor.fetchall()
        return result
    except Error as e:
        logger.error(f"执行查询失败: {str(e)}")
        if local_conn and not conn:
            local_conn.rollback()
        raise DBException(f"执行查询失败: {str(e)}")
    finally:
        if not cursor and local_cursor:
            local_cursor.close()
        if not conn and local_conn:
            local_conn.close()


def begin_transaction():
    """开始事务
    
    Returns:
        tuple: (conn, cursor) 数据库连接和游标对象
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        conn.start_transaction()
        logger.info("事务开始")
        return conn, cursor
    except Error as e:
        logger.error(f"开始事务失败: {str(e)}")
        if conn:
            conn.close()
        raise DBException(f"开始事务失败: {str(e)}")


def commit_transaction(conn, cursor):
    """提交事务
    
    Args:
        conn: 数据库连接对象
        cursor: 游标对象
    """
    try:
        conn.commit()
        logger.info("事务提交成功")
    except Error as e:
        logger.error(f"提交事务失败: {str(e)}")
        raise DBException(f"提交事务失败: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def rollback_transaction(conn, cursor):
    """回滚事务
    
    Args:
        conn: 数据库连接对象
        cursor: 游标对象
    """
    try:
        conn.rollback()
        logger.info("事务回滚成功")
    except Error as e:
        logger.error(f"回滚事务失败: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def create_tables():
    """创建必要的表结构
    
    如果表不存在，创建 aiuser_talk 和 aiuser_message 表
    """
    try:
        # 创建 aiuser_talk 表
        talk_table_query = """
        CREATE TABLE IF NOT EXISTS aiuser_talk (
            id INT AUTO_INCREMENT PRIMARY KEY,
            session_id VARCHAR(255) UNIQUE NOT NULL,
            user_id VARCHAR(255),
            title VARCHAR(255),
            start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            end_time DATETIME,
            message_count INT DEFAULT 0,
            course VARCHAR(255),
            status VARCHAR(50) DEFAULT 'active'
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        execute_update(talk_table_query)
        logger.info("aiuser_talk 表检查/创建成功")
        
        # 创建 aiuser_message 表
        message_table_query = """
        CREATE TABLE IF NOT EXISTS aiuser_message (
            id INT AUTO_INCREMENT PRIMARY KEY,
            conversation_id VARCHAR(255) NOT NULL,
            content TEXT NOT NULL,
            message_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            sender VARCHAR(50) NOT NULL,
            FOREIGN KEY (conversation_id) REFERENCES aiuser_talk(session_id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        execute_update(message_table_query)
        logger.info("aiuser_message 表检查/创建成功")
        
    except Exception as e:
        logger.error(f"创建表失败: {str(e)}")
        raise DBException(f"创建表失败: {str(e)}")


if __name__ == "__main__":
    """测试数据库连接和表创建"""
    try:
        create_tables()
        logger.info("数据库初始化完成")
    except Exception as e:
        logger.error(f"测试失败: {str(e)}")
