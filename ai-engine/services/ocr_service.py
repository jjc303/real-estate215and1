"""OCR service backed by Alibaba Bailian OCR models."""

from __future__ import annotations

import asyncio
import base64
from typing import Any, Optional

import httpx

from config.config import settings
from prompts import build_ocr_prompt
from services.base import BaseService
from utils.exceptions import ErrorCode, OCRException


class OCRService(BaseService):
    """Recognize text from images through Bailian OCR."""

    OCR_PATH = "/api/v1/services/aigc/multimodal-generation/generation"

    def __init__(self):
        super().__init__()
        self._client: Optional[httpx.AsyncClient] = None

    def initialize(self) -> bool:
        try:
            self._log_info("初始化 OCR 服务...")
            self._client = httpx.AsyncClient(timeout=settings.OCR_TIMEOUT_SECONDS)
            return True
        except Exception as error:
            self._log_error("初始化 OCR 服务失败", error)
            return False

    def health_check(self) -> dict:
        if not self._client:
            return {"status": "warning", "message": "OCR 服务未初始化", "model": settings.OCR_MODEL}
        return {
            "status": "ok",
            "message": "OCR 服务运行正常",
            "model": settings.OCR_MODEL,
            "timeout_seconds": settings.OCR_TIMEOUT_SECONDS,
        }

    def shutdown(self):
        try:
            self._log_info("关闭 OCR 服务...")
            if self._client:
                client = self._client
                self._client = None

                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    asyncio.run(client.aclose())
                else:
                    loop.create_task(client.aclose())

            self._log_info("OCR 服务关闭成功")
        except Exception as error:
            self._log_error("关闭 OCR 服务失败", error)

    async def recognize_text(
        self,
        image_bytes: bytes,
        language: str = "zh",
        enable_formula: bool = False,
        mime_type: str = "image/jpeg",
    ) -> dict[str, Any]:
        try:
            if not self._client:
                raise OCRException("OCR 服务未初始化", ErrorCode.OCR_ERROR)

            if not isinstance(image_bytes, (bytes, bytearray)):
                raise OCRException("图片数据格式无效，必须为 bytes", ErrorCode.OCR_ERROR)

            if not image_bytes:
                raise OCRException("图片数据不能为空", ErrorCode.OCR_ERROR)

            response = await self._request_ocr(
                image_bytes=bytes(image_bytes),
                language=language,
                enable_formula=enable_formula,
                mime_type=mime_type,
            )
            return self._normalize_ocr_result(response, language=language)
        except OCRException:
            raise
        except httpx.HTTPError as error:
            self._log_error("OCR 请求失败", error)
            raise OCRException(f"OCR 请求失败: {error}", ErrorCode.OCR_ERROR)
        except Exception as error:
            self._log_error("OCR 处理失败", error)
            raise OCRException(f"OCR 处理失败: {error}", ErrorCode.OCR_ERROR)

    async def _request_ocr(
        self,
        *,
        image_bytes: bytes,
        language: str,
        enable_formula: bool,
        mime_type: str,
    ) -> dict[str, Any]:
        if not self._client:
            raise OCRException("OCR 服务未初始化", ErrorCode.OCR_ERROR)

        mime_type = (mime_type or "image/jpeg").strip().lower()
        if not mime_type.startswith("image/"):
            mime_type = "image/jpeg"

        data_url = f"data:{mime_type};base64,{base64.b64encode(image_bytes).decode('utf-8')}"
        payload = {
            "model": settings.OCR_MODEL,
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"image": data_url},
                            {"text": build_ocr_prompt(language=language, enable_formula=enable_formula)},
                        ],
                    }
                ]
            },
            "parameters": {
                "ocr_options": {
                    "task": self._resolve_task(enable_formula=enable_formula, language=language),
                },
            },
        }
        headers = {
            "Authorization": f"Bearer {settings.DASHSCOPE_API_KEY}",
            "Content-Type": "application/json",
        }
        url = f"{settings.DASHSCOPE_BASE_URL.rstrip('/')}{self.OCR_PATH}"

        last_error: Optional[Exception] = None
        max_retries = max(1, int(settings.OCR_MAX_RETRIES))

        for attempt in range(max_retries):
            try:
                response = await self._client.post(url, json=payload, headers=headers)

                if response.status_code >= 400:
                    self._log_error(
                        "百炼 OCR 请求失败",
                        Exception(f"status={response.status_code}, body={response.text}"),
                    )

                response.raise_for_status()
                body = response.json()

                if body.get("code"):
                    raise OCRException(
                        f"百炼 OCR 返回错误: {body.get('message') or body.get('code')}",
                        ErrorCode.OCR_ERROR,
                    )

                return body

            except OCRException as error:
                last_error = error
                raise

            except (httpx.TimeoutException, httpx.NetworkError, httpx.TransportError) as error:
                last_error = error
                if attempt < max_retries - 1:
                    await asyncio.sleep(2**attempt)
                    continue
                break

            except httpx.HTTPStatusError as error:
                last_error = error
                status_code = error.response.status_code if error.response else None

                if status_code is not None and status_code >= 500 and attempt < max_retries - 1:
                    await asyncio.sleep(2**attempt)
                    continue
                break

            except Exception as error:
                last_error = error
                break

        if isinstance(last_error, OCRException):
            raise last_error
        raise OCRException(f"调用百炼 OCR 失败: {last_error}", ErrorCode.OCR_ERROR)

    def _resolve_task(self, *, enable_formula: bool, language: str) -> str:
        if enable_formula:
            return "formula_recognition"
        if language.startswith("zh"):
            return "advanced_recognition"
        return "multi_lan"

    def _normalize_ocr_result(self, payload: dict[str, Any], language: str) -> dict[str, Any]:
        output = payload.get("output", {})
        choices = output.get("choices", [])

        if not isinstance(choices, list) or not choices:
            raise OCRException("OCR 返回结构异常：缺少 output.choices", ErrorCode.OCR_ERROR)

        message = choices[0].get("message", {})
        content = message.get("content", [])

        if not isinstance(content, list) or not content:
            raise OCRException("OCR 返回结构异常：缺少 message.content", ErrorCode.OCR_ERROR)

        content_item = content[0] if isinstance(content[0], dict) else {}

        # 优先使用结构化 OCR 结果
        ocr_result = content_item.get("ocr_result") or {}
        words_info = ocr_result.get("words_info") or []

        items = []
        fragments = []
        confidences = []

        for word_info in words_info:
            if not isinstance(word_info, dict):
                continue

            text = str(word_info.get("text") or "").strip()
            if not text:
                continue

            fragments.append(text)

            item = {"text": text}

            confidence = word_info.get("confidence")
            if isinstance(confidence, (int, float)):
                item["confidence"] = float(confidence)
                confidences.append(float(confidence))

            bbox = self._normalize_bbox(word_info.get("location"))
            if bbox is not None:
                item["bbox"] = bbox

            items.append(item)

        full_text = str(ocr_result.get("text") or "").strip()
        if not full_text and fragments:
            joiner = "" if language.startswith("zh") else " "
            full_text = joiner.join(fragments)

        # 降级：若没有结构化 OCR 结果，则尝试拿纯文本
        if not full_text:
            fallback_text = content_item.get("text")
            if isinstance(fallback_text, str):
                full_text = fallback_text.strip()

        if not items and full_text:
            items = [{"text": full_text}]

        normalized = {"text": full_text, "items": items}
        if confidences:
            normalized["confidence"] = sum(confidences) / len(confidences)

        return normalized

    def _normalize_bbox(self, location: Any) -> Optional[list[list[float]]]:
        if not isinstance(location, list):
            return None

        if len(location) == 4 and all(isinstance(value, (int, float)) for value in location):
            x1, y1, x2, y2 = location
            return [
                [float(x1), float(y1)],
                [float(x2), float(y1)],
                [float(x2), float(y2)],
                [float(x1), float(y2)],
            ]

        if len(location) == 8 and all(isinstance(value, (int, float)) for value in location):
            return [
                [float(location[0]), float(location[1])],
                [float(location[2]), float(location[3])],
                [float(location[4]), float(location[5])],
                [float(location[6]), float(location[7])],
            ]

        if all(isinstance(point, list) and len(point) == 2 for point in location):
            return [[float(point[0]), float(point[1])] for point in location]

        return None
