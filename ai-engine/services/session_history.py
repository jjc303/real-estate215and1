"""会话历史管理模块

本文件负责管理AI对话的会话历史，包括：
1. 会话历史的缓存管理
2. 会话历史的数据库持久化
3. 会话历史的加载和保存
4. 提供统一的会话历史接口

使用内存缓存和数据库持久化的双层存储策略，
既保证性能又确保数据安全。
"""

# 标准库
import datetime
import time
import threading

# 第三方库
from langchain_community.chat_message_histories import ChatMessageHistory

# 本地模块
from config.config import settings
from utils.db import (
    begin_transaction,
    commit_transaction,
    create_tables,
    execute_query,
    execute_update,
    rollback_transaction,
)
from utils.exceptions import SessionException
from utils.async_utils import AsyncExecutionHelper
from services.base import BaseService

class SessionHistoryCache(BaseService):
    """会话历史缓存类"""
    def __init__(self, max_size=None, expire_seconds=None):
        """
        初始化缓存
        
        Args:
            max_size: 缓存最大会话数，默认从配置读取
            expire_seconds: 缓存过期时间（秒），默认从配置读取
        """
        super().__init__()
        self.cache = {}
        self.max_size = max_size or settings.HISTORY_CACHE_MAX_SIZE
        self.expire_seconds = expire_seconds or settings.HISTORY_CACHE_EXPIRE_SECONDS
        self.lock = threading.Lock()
        self._tables_initialized = False
    
    def get(self, session_id):
        """获取缓存的会话历史
        
        Args:
            session_id: 会话ID
        
        Returns:
            ChatMessageHistory 实例或 None
        """
        with self.lock:
            if session_id in self.cache:
                history, timestamp = self.cache[session_id]
                # 检查是否过期
                if time.time() - timestamp < self.expire_seconds:
                    self._log_info(f"从缓存加载会话历史: {session_id}")
                    return history
                else:
                    # 缓存过期，删除
                    del self.cache[session_id]
            return None
    
    def set(self, session_id, history):
        """设置缓存的会话历史
        
        Args:
            session_id: 会话ID
            history: ChatMessageHistory 实例
        """
        with self.lock:
            # 检查缓存大小
            if len(self.cache) >= self.max_size:
                # 删除最早的缓存
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
                self._log_info(f"缓存达到上限，删除最早的会话: {oldest_key}")
            # 设置缓存
            self.cache[session_id] = (history, time.time())
            self._log_info(f"缓存会话历史: {session_id}")
    
    def initialize(self) -> bool:
        """初始化会话历史缓存服务"""
        try:
            self._log_info("初始化会话历史缓存服务...")
            if not self._tables_initialized:
                create_tables()
                self._tables_initialized = True
                self._log_info("数据库表结构初始化成功")
            # 检查配置值是否有效
            if self.max_size <= 0:
                self._log_warning("缓存最大大小配置无效，使用默认值")
                self.max_size = 1000
            if self.expire_seconds <= 0:
                self._log_warning("缓存过期时间配置无效，使用默认值")
                self.expire_seconds = 3600
            self._log_info(f"会话历史缓存服务初始化完成，最大大小: {self.max_size}，过期时间: {self.expire_seconds}秒")
            return True
        except Exception as e:
            self._log_error("初始化会话历史缓存服务失败", e)
            return False
    
    def health_check(self) -> dict:
        """健康检查
        
        Returns:
            dict: 健康检查结果
        """
        try:
            with self.lock:
                cache_size = len(self.cache)
                return {
                    "status": "ok",
                    "message": f"会话历史缓存服务运行正常，当前缓存大小: {cache_size}/{self.max_size}",
                    "cache_size": cache_size,
                    "max_size": self.max_size,
                    "expire_seconds": self.expire_seconds
                }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def shutdown(self):
        """关闭服务
        
        释放服务占用的资源
        """
        try:
            self._log_info("关闭会话历史缓存服务...")
            # 清空缓存
            with self.lock:
                self.cache.clear()
            self._log_info("会话历史缓存服务关闭成功")
        except Exception as e:
            self._log_error("关闭会话历史缓存服务失败", e)
    
    def clear_session(self, session_id: str):
        """清除指定会话的缓存
        
        Args:
            session_id: 会话ID
        """
        with self.lock:
            if session_id in self.cache:
                del self.cache[session_id]
                self._log_info(f"清除缓存中的会话历史: {session_id}")
    
    def get_history_obj(self, session_id: str, limit: int = 20):
        """获取会话历史对象
        
        Args:
            session_id: 会话ID
            limit: 消息数量限制
            
        Returns:
            ChatMessageHistory 实例
        """
        # 尝试从缓存获取
        cached_history = self.get(session_id)
        if cached_history:
            return cached_history
        
        # 缓存未命中，从数据库加载
        history = ChatMessageHistory()
        try:
            query = """
            SELECT content, sender, message_time 
            FROM aiuser_message 
            WHERE conversation_id = %s 
            ORDER BY message_time ASC
            LIMIT %s
            """
            messages = execute_query(query, (session_id, limit))
            
            for msg in messages:
                if msg['sender'] == 'user':
                    history.add_user_message(msg['content'])
                elif msg['sender'] == 'ai':
                    history.add_ai_message(msg['content'])
            
            self._log_info(f"从数据库加载会话历史，共 {len(messages)} 条消息")
            
            # 缓存会话历史
            self.set(session_id, history)
            
        except Exception as e:
            self._log_error(f"加载会话历史失败: {str(e)}")
            raise SessionException(f"加载会话历史失败: {str(e)}", 500)
        
        return history

    async def aget_history_obj(self, session_id: str, limit: int = 20):
        """在线程中加载会话历史对象，避免异步链路直接阻塞数据库查询。"""
        return await AsyncExecutionHelper.run_blocking(
            self.get_history_obj,
            session_id,
            limit,
        )
    
    def save_message(self, session_id: str, content: str, sender: str, course: str, user_id: str = None, conn=None, cursor=None):
        """保存消息到数据库
        
        Args:
            session_id: 会话ID
            content: 消息内容
            sender: 发送者 (user/ai)
            course: 课程名称
            user_id: 用户ID
            conn: 数据库连接对象（可选，用于事务）
            cursor: 游标对象（可选，用于事务）
        """
        try:
            # 使用 INSERT IGNORE 避免并发冲突
            insert_session_query = """
            INSERT IGNORE INTO aiuser_talk (session_id, user_id, course, start_time, message_count, status)
            VALUES (%s, %s, %s, %s, 0, 'active')
            """
            affected_rows = execute_update(insert_session_query, (session_id, user_id, course, datetime.datetime.now()), conn, cursor)
            if affected_rows > 0:
                self._log_info(f"创建新会话: {session_id}, 用户: {user_id}")
            
            insert_message_query = """
            INSERT INTO aiuser_message (conversation_id, content, sender, message_time)
            VALUES (%s, %s, %s, %s)
            """
            execute_update(insert_message_query, (session_id, content, sender, datetime.datetime.now()), conn, cursor)
            
            update_count_query = """
            UPDATE aiuser_talk 
            SET message_count = message_count + 1, end_time = %s 
            WHERE session_id = %s
            """
            execute_update(update_count_query, (datetime.datetime.now(), session_id), conn, cursor)
            
        except Exception as e:
            self._log_error(f"保存消息失败: {str(e)}")
            raise SessionException(f"保存消息失败: {str(e)}", 500)
    
    def save_user_message(self, session_id: str, content: str, course: str, user_id: str = None, conn=None, cursor=None):
        """保存用户消息
        
        Args:
            session_id: 会话ID
            content: 消息内容
            course: 课程名称
            user_id: 用户ID
            conn: 数据库连接对象（可选，用于事务）
            cursor: 游标对象（可选，用于事务）
        """
        self.save_message(session_id, content, 'user', course, user_id, conn, cursor)

    async def asave_user_message(self, session_id: str, content: str, course: str, user_id: str = None, conn=None, cursor=None):
        """异步包装的用户消息保存入口。"""
        await AsyncExecutionHelper.run_blocking(
            self.save_user_message,
            session_id,
            content,
            course,
            user_id,
            conn,
            cursor,
        )
    
    def save_ai_message(self, session_id: str, content: str, course: str, user_id: str = None, conn=None, cursor=None):
        """保存AI消息
        
        Args:
            session_id: 会话ID
            content: 消息内容
            course: 课程名称
            user_id: 用户ID
            conn: 数据库连接对象（可选，用于事务）
            cursor: 游标对象（可选，用于事务）
        """
        self.save_message(session_id, content, 'ai', course, user_id, conn, cursor)

    async def asave_ai_message(self, session_id: str, content: str, course: str, user_id: str = None, conn=None, cursor=None):
        """异步包装的 AI 消息保存入口。"""
        await AsyncExecutionHelper.run_blocking(
            self.save_ai_message,
            session_id,
            content,
            course,
            user_id,
            conn,
            cursor,
        )

    def save_chat_round(
        self,
        session_id: str,
        question: str,
        answer: str,
        course: str,
        user_id: str = None,
    ):
        """以单事务保存一轮完整对话。"""
        conn = None
        cursor = None
        try:
            conn, cursor = begin_transaction()
            self.save_user_message(session_id, question, course, user_id, conn, cursor)
            self.save_ai_message(session_id, answer, course, user_id, conn, cursor)
            commit_transaction(conn, cursor)
            self._log_info(f"完整对话落库成功: {session_id}")
        except Exception as e:
            if conn and cursor:
                try:
                    rollback_transaction(conn, cursor)
                except Exception as rollback_error:
                    self._log_error("回滚完整对话事务失败", rollback_error)
            self._log_error(f"保存完整对话失败: {str(e)}")
            raise SessionException(f"保存完整对话失败: {str(e)}", 500)

    async def asave_chat_round(
        self,
        session_id: str,
        question: str,
        answer: str,
        course: str,
        user_id: str = None,
    ):
        """异步包装的完整对话落库入口。"""
        await AsyncExecutionHelper.run_blocking(
            self.save_chat_round,
            session_id,
            question,
            answer,
            course,
            user_id,
        )
    
    def update_cache(self, session_id: str, user_message: str, ai_response: str):
        """更新缓存中的会话历史
        
        Args:
            session_id: 会话ID
            user_message: 用户消息
            ai_response: AI回答
        """
        cached_history = self.get(session_id)
        if cached_history:
            cached_history.add_user_message(user_message)
            cached_history.add_ai_message(ai_response)
            self.set(session_id, cached_history)
            self._log_info(f"更新缓存中的会话历史: {session_id}")
    

    
    def get_session_info(self, session_id: str):
        """获取会话信息
        
        Args:
            session_id: 会话ID
            
        Returns:
            会话信息字典或 None
        """
        try:
            query = """
            SELECT * FROM aiuser_talk WHERE session_id = %s
            """
            result = execute_query(query, (session_id,))
            return result[0] if result else None
        except Exception as e:
            self._log_error(f"获取会话信息失败: {str(e)}")
            raise SessionException(f"获取会话信息失败: {str(e)}", 500)
    
    def get_history_text(self, session_id: str, limit: int = 20):
        """获取会话历史文本
        
        Args:
            session_id: 会话ID
            limit: 消息数量限制
            
        Returns:
            会话历史文本
        """
        try:
            history = self.get_history_obj(session_id, limit)
            if not history:
                return ""
            
            # 构建历史文本
            history_text = ""
            for i, message in enumerate(history.messages):
                if hasattr(message, 'type') and message.type == 'human':
                    history_text += f"用户: {message.content}\n"
                elif hasattr(message, 'type') and message.type == 'ai':
                    history_text += f"AI: {message.content}\n"
            
            return history_text
        except Exception as e:
            self._log_error(f"获取历史对话失败: {str(e)}")
            return ""

    async def aget_history_text(self, session_id: str, limit: int = 20):
        """在线程中拼接历史文本，供异步服务链路统一调用。"""
        return await AsyncExecutionHelper.run_blocking(
            self.get_history_text,
            session_id,
            limit,
        )
