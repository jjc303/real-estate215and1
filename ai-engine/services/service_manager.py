"""Service manager for the rental AI engine."""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Set

from config.config import settings
from services.base import BaseService
from services.embedding_service import EmbeddingService
from services.llm_service import LLMService
from services.ocr_service import OCRService
from services.rag.manager import RAGManager
from services.rental_service import RentalService
from services.session_history import SessionHistoryCache
from utils.async_utils import AsyncExecutionHelper
from utils.logger import get_logger


class ServiceManager:
    """Manage lifecycle and dependencies of shared AI services."""

    def __init__(self):
        self._services: Dict[str, BaseService] = {}
        self._dependencies: Dict[str, List[str]] = {}
        self._initialized: Dict[str, bool] = {}
        self._init_order: List[str] = []
        self._last_event: Dict[str, str] = {}
        self._recent_error: Dict[str, Optional[str]] = {}
        self._logger = get_logger(__name__)
        self._initialize_default_services()

    def _initialize_default_services(self):
        self.register_service("embedding", EmbeddingService())
        self.register_service("llm", LLMService())
        self.register_service("ocr", OCRService())
        self.register_service("session_history", SessionHistoryCache())
        self.register_service("rag", RAGManager(), dependencies=["embedding"])
        self.register_service(
            "rental",
            RentalService(),
            dependencies=["llm", "session_history"],
        )

    def register_service(
        self,
        name: str,
        service: BaseService,
        dependencies: Optional[List[str]] = None,
    ):
        if not isinstance(service, BaseService):
            raise ValueError(f"Service must inherit BaseService: {service}")
        self._services[name] = service
        self._dependencies[name] = list(dependencies or [])
        self._initialized[name] = False
        self._last_event[name] = "registered"
        self._recent_error[name] = None
        self._logger.info(f"Service registered: {name}")

    def get_service(self, name: str, require_initialized: bool = False) -> Optional[BaseService]:
        service = self._services.get(name)
        if not service:
            return None
        if require_initialized and not self.initialize_service(name):
            return None
        return service

    def is_initialized(self, name: str) -> bool:
        return bool(self._initialized.get(name))

    def get_service_dependencies(self, name: str) -> List[str]:
        return list(self._dependencies.get(name, []))

    def initialize_service(self, name: str, initializing: Optional[Set[str]] = None) -> bool:
        service = self._services.get(name)
        if not service:
            self._logger.error(f"Service not found: {name}")
            return False
        if self._initialized.get(name):
            return True

        stack = initializing or set()
        if name in stack:
            raise RuntimeError(f"Cyclic dependency detected: {name}")
        stack.add(name)

        try:
            for dependency in self._dependencies.get(name, []):
                if not self.initialize_service(dependency, stack):
                    self._last_event[name] = "dependency_failed"
                    self._recent_error[name] = f"Dependency failed: {dependency}"
                    return False

            initialized = service.initialize()
            self._initialized[name] = bool(initialized)
            if initialized:
                if name not in self._init_order:
                    self._init_order.append(name)
                self._last_event[name] = "initialized"
                self._recent_error[name] = None
                return True

            self._last_event[name] = "initialize_failed"
            self._recent_error[name] = "initialize returned False"
            return False
        except Exception as exc:
            self._initialized[name] = False
            self._last_event[name] = "initialize_failed"
            self._recent_error[name] = str(exc)
            self._logger.error(f"Service initialization failed: {name}, error: {exc}")
            return False
        finally:
            stack.discard(name)

    def initialize_all(self) -> bool:
        settings.validate_runtime_config()
        success = True
        for name in self._services:
            if not self.initialize_service(name):
                success = False
        return success

    async def initialize_all_async(self) -> bool:
        return await AsyncExecutionHelper.run_blocking(self.initialize_all)

    def health_check_all(self) -> Dict[str, Dict]:
        results = {}
        for name, service in self._services.items():
            try:
                health = service.health_check()
                health["initialized"] = self.is_initialized(name)
                if health.get("status") == "error":
                    self._recent_error[name] = str(health.get("message", ""))
                results[name] = health
            except Exception as exc:
                self._last_event[name] = "health_check_failed"
                self._recent_error[name] = str(exc)
                results[name] = {"status": "error", "message": str(exc)}
        return results

    def get_runtime_status(self) -> Dict[str, object]:
        health_results = self.health_check_all()
        services = []
        healthy_services = 0
        warning_services = 0
        error_services = 0
        initialized_services = 0
        degraded_services: List[str] = []
        unavailable_services: List[str] = []

        for name in self._services:
            health = health_results.get(name, {})
            status = str(health.get("status", "unknown"))
            message = str(health.get("message", ""))
            initialized = self.is_initialized(name)
            details = {
                key: value
                for key, value in health.items()
                if key not in {"status", "message", "initialized"}
            }
            if initialized:
                initialized_services += 1
            if status == "ok":
                healthy_services += 1
            elif status == "warning":
                warning_services += 1
                degraded_services.append(name)
            else:
                error_services += 1
                degraded_services.append(name)
            if not initialized or status == "error":
                unavailable_services.append(name)
            services.append(
                {
                    "name": name,
                    "initialized": initialized,
                    "status": status,
                    "message": message,
                    "dependencies": self.get_service_dependencies(name),
                    "details": details,
                    "last_event": self._last_event.get(name),
                    "recent_error": self._recent_error.get(name),
                }
            )

        total_services = len(self._services)
        if total_services == 0:
            overall_status = "unknown"
        elif error_services == 0 and warning_services == 0 and initialized_services == total_services:
            overall_status = "ok"
        elif initialized_services == 0 and error_services > 0:
            overall_status = "error"
        else:
            overall_status = "degraded"

        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "summary": self._build_runtime_summary(
                overall_status=overall_status,
                total_services=total_services,
                initialized_services=initialized_services,
                degraded_services=degraded_services,
                unavailable_services=unavailable_services,
            ),
            "overall_status": overall_status,
            "total_services": total_services,
            "initialized_services": initialized_services,
            "healthy_services": healthy_services,
            "warning_services": warning_services,
            "error_services": error_services,
            "degraded_services": degraded_services,
            "unavailable_services": unavailable_services,
            "services": services,
        }

    def _build_runtime_summary(
        self,
        *,
        overall_status: str,
        total_services: int,
        initialized_services: int,
        degraded_services: List[str],
        unavailable_services: List[str],
    ) -> str:
        if total_services == 0:
            return "当前没有已注册服务。"
        if overall_status == "ok":
            return f"租房 AI 引擎运行正常，全部 {total_services} 个服务已就绪。"
        if overall_status == "error":
            return "租房 AI 引擎异常，当前核心服务尚未准备完成。"
        parts = [f"租房 AI 引擎处于降级模式，已初始化 {initialized_services}/{total_services} 个服务"]
        if degraded_services:
            parts.append(f"异常或告警服务：{', '.join(degraded_services)}")
        if unavailable_services:
            parts.append(f"当前不可用：{', '.join(unavailable_services)}")
        return "；".join(parts) + "。"

    async def health_check_all_async(self) -> Dict[str, Dict]:
        results = {}
        for name, service in self._services.items():
            try:
                results[name] = await service.health_check_async()
            except Exception as exc:
                results[name] = {"status": "error", "message": str(exc)}
        return results

    def shutdown_all(self):
        for name in reversed(self._init_order or list(self._services.keys())):
            service = self._services.get(name)
            if not service:
                continue
            try:
                service.shutdown()
                self._initialized[name] = False
                self._last_event[name] = "shutdown"
            except Exception as exc:
                self._last_event[name] = "shutdown_failed"
                self._recent_error[name] = str(exc)
                self._logger.error(f"Service shutdown failed: {name}, error: {exc}")
        self._init_order.clear()

    async def shutdown_all_async(self):
        for name, service in self._services.items():
            try:
                await service.shutdown_async()
            except Exception as exc:
                self._logger.error(f"Service async shutdown failed: {name}, error: {exc}")


service_manager = ServiceManager()
