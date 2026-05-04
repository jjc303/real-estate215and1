"""OCR 文本识别接口。

本模块负责接收图片文本识别请求，并调用 OCR 服务生成识别结果。
它保持路由层轻量，只做参数校验、服务转发和响应包装。
"""

from typing import Any, List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field

from api.dependencies import get_required_service
from api.schemas.common import ApiResponse, success_response
from utils.auth import verify_api_key
from utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/jpg", "image/webp"}


class OCRItem(BaseModel):
    """OCR 识别结果项。"""

    text: str  # 识别的文本内容
    confidence: Optional[float] = None  # 识别置信度
    bbox: Optional[Any] = None  # 文本边界框坐标


class OCRResult(BaseModel):
    """OCR 识别结果。"""

    text: str  # 完整识别文本
    items: List[OCRItem] = Field(default_factory=list)  # 识别的文本项列表
    confidence: Optional[float] = None  # 整体识别置信度


@router.post(
    "/ocr/recognize",
    summary="OCR 文本识别接口",
    response_model=ApiResponse[OCRResult],
    description="""识别图片中的文本内容，内部使用阿里百炼 OCR 模型，
但对外仍保持统一的 text/items/confidence 响应结构。

**功能说明**：
- 支持识别图片中的文本内容
- 支持多种语言识别
- 可选启用公式识别
- 返回完整识别文本和详细的文本项列表

**请求参数**：
- image: 上传的图片文件
- language: 语言类型，默认为 "zh"（中文）
- enable_formula: 是否启用公式识别，默认为 False

**响应示例**：
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "text": "Hello World! 你好，世界！",
    "items": [
      {
        "text": "Hello World!",
        "confidence": 0.99,
        "bbox": [10, 10, 100, 30]
      },
      {
        "text": "你好，世界！",
        "confidence": 0.98,
        "bbox": [10, 40, 100, 60]
      }
    ],
    "confidence": 0.985
  }
}
```
"""
)
async def ocr_recognize(
    image: UploadFile = File(...),
    language: str = Form("zh"),
    enable_formula: bool = Form(False),
    api_key: str = Depends(verify_api_key),
):
    """处理 OCR 文本识别请求并返回统一格式的识别结果。"""

    try:
        # 路由层统一通过 helper 获取服务，减少重复的 503 判空逻辑。
        ocr_service = get_required_service("ocr", "OCR服务")

        if image.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件类型: {image.content_type}。仅支持: {', '.join(sorted(ALLOWED_IMAGE_TYPES))}"
            )

        image_bytes = await image.read()

        if not image_bytes:
            raise HTTPException(status_code=400, detail="上传文件为空")

        if len(image_bytes) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"文件过大: {len(image_bytes) / 1024 / 1024:.2f}MB，最大允许: {MAX_FILE_SIZE / 1024 / 1024:.2f}MB"
            )

        # 具体的 OCR 识别逻辑在服务层完成。
        result = await ocr_service.recognize_text(
            image_bytes=image_bytes,
            language=language,
            enable_formula=enable_formula,
            mime_type=image.content_type,
        )
        return success_response(OCRResult(**result))
    except HTTPException:
        raise
    except Exception as error:
        logger.error(f"OCR 识别失败: {error}")
        raise