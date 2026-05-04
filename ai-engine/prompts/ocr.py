"""OCR Prompt 模板。"""


def build_ocr_prompt(*, language: str, enable_formula: bool) -> str:
    """构建 OCR 识别提示词。"""
    if enable_formula:
        if language.startswith("zh"):
            return "请仅提取图片中的文本和公式，按阅读顺序返回，不要添加解释，不要使用 Markdown。"
        return "Extract only the visible text and formulas in reading order. Do not add explanations. Do not use Markdown."

    if language.startswith("zh"):
        return "请仅提取图片中的可见文字，按阅读顺序返回，不要添加解释，不要使用 Markdown。"
    return "Extract only the visible text in reading order. Do not add explanations. Do not use Markdown."
