"""LLM 服务模块。

本模块统一封装大模型的初始化、健康检查和调用方式，
为聊天、批改等上层能力提供一致的模型访问入口。
"""

from langchain_community.chat_models import ChatTongyi
from utils.logger import get_logger
from utils.exceptions import LLMException
from config.config import settings
from services.base import BaseService


class LLMService(BaseService):
    """统一管理大模型实例的服务。"""
    
    def __init__(self):
        """初始化 LLM 服务。"""
        super().__init__()
        self.llm = None
    
    def initialize(self) -> bool:
        """初始化 LLM 服务。"""
        try:
            # 统一在这里创建模型实例，避免各业务服务重复配置模型参数。
            self.llm = ChatTongyi(
                model_name=settings.LLM_MODEL,  # 模型名称
                temperature=settings.LLM_TEMPERATURE,  # 温度参数，控制输出随机性
                openai_api_key=settings.DASHSCOPE_API_KEY,  # DashScope API 密钥
                openai_api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",  # 兼容模式接口地址
            )
            
            self._log_info(f"LLM服务初始化成功，模型: {settings.LLM_MODEL}")
            return True
        except Exception as e:
            self._log_error("LLM服务初始化失败", e)
            return False
    
    def health_check(self) -> dict:
        """返回 LLM 服务当前健康状态。"""
        try:
            # 模型对象不存在时，说明初始化流程尚未成功完成。
            if not self.llm:
                return {"status": "error", "message": "LLM模型未初始化"}
            
            return {
                "status": "ok",
                "message": "LLM服务运行正常",
                "model": settings.LLM_MODEL,
                "temperature": settings.LLM_TEMPERATURE,
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def shutdown(self):
        """关闭 LLM 服务并释放运行期资源。"""
        try:
            self._log_info("关闭LLM服务...")
            # 当前模型对象可按需重建，关闭时直接释放引用即可。
            self.llm = None
            self._log_info("LLM服务关闭成功")
        except Exception as e:
            self._log_error("关闭LLM服务失败", e)
    
    def invoke(self, prompt):
        """同步调用大模型并返回文本结果。"""
        try:
            if not self.llm:
                raise LLMException("LLM模型未初始化", 500)

            # 对上层统一返回 content，避免业务侧感知底层响应对象结构。
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            self._log_error("调用LLM失败", e)
            if isinstance(e, LLMException):
                raise
            raise LLMException(f"调用LLM失败：{str(e)}")
    
    async def ainvoke(self, prompt):
        """异步调用大模型并返回文本结果。"""
        try:
            if not self.llm:
                raise LLMException("LLM模型未初始化", 500)

            # 异步接口用于批改、聊天等需要非阻塞调用的场景。
            response = await self.llm.ainvoke(prompt)
            return response.content
        except Exception as e:
            self._log_error("异步调用LLM失败", e)
            if isinstance(e, LLMException):
                raise
            raise LLMException(f"异步调用LLM失败：{str(e)}")
    
    def generate(self, prompt):
        """`invoke` 的语义化别名。"""
        return self.invoke(prompt)
    
    async def agenerate(self, prompt):
        """`ainvoke` 的语义化别名。"""
        return await self.ainvoke(prompt)