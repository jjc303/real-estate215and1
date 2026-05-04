"""Unit tests for OCR service normalization."""

import pytest

from services.ocr_service import OCRService


pytestmark = pytest.mark.unit


def test_normalize_ocr_result_keeps_bbox_and_text():
    service = OCRService()
    payload = {
        "output": {
            "choices": [
                {
                    "message": {
                        "content": [
                            {
                                "ocr_result": {
                                    "text": "第一行\n第二行",
                                    "words_info": [
                                        {
                                            "text": "第一行",
                                            "confidence": 0.95,
                                            "location": [10, 20, 110, 60],
                                        },
                                        {
                                            "text": "第二行",
                                            "confidence": 0.85,
                                            "location": [10, 70, 110, 110],
                                        },
                                    ],
                                }
                            }
                        ]
                    }
                }
            ]
        }
    }

    result = service._normalize_ocr_result(payload, language="zh")

    assert result["text"] == "第一行\n第二行"
    assert len(result["items"]) == 2
    assert result["items"][0]["bbox"] == [[10.0, 20.0], [110.0, 20.0], [110.0, 60.0], [10.0, 60.0]]
    assert result["confidence"] == pytest.approx(0.9)


def test_normalize_ocr_result_falls_back_without_location():
    service = OCRService()
    payload = {
        "output": {
            "choices": [
                {
                    "message": {
                        "content": [
                            {
                                "ocr_result": {
                                    "words_info": [
                                        {"text": "hello"},
                                        {"text": "world"},
                                    ]
                                }
                            }
                        ]
                    }
                }
            ]
        }
    }

    result = service._normalize_ocr_result(payload, language="en")

    assert result["text"] == "hello world"
    assert result["items"] == [{"text": "hello"}, {"text": "world"}]
    assert "confidence" not in result
