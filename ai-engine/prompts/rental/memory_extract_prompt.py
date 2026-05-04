"""Prompt for extracting rental preference memory."""

from langchain_core.prompts import ChatPromptTemplate


class RentalMemoryExtractPrompt:
    """Build prompt for extracting long-term rental preferences."""

    @staticmethod
    def build() -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "你负责从用户对话中提取长期有用的租房偏好记忆。\n"
                    "只允许提取以下类型：budget_preference、region_preference、house_type_preference、"
                    "area_preference、commute_preference、facility_preference、decoration_preference、"
                    "floor_preference、rental_constraint、avoid_preference。\n"
                    "禁止提取或保存：身份证号、手机号、银行卡、精确住址、真实姓名、合同编号、签名、其他敏感个人信息。\n"
                    "如果没有可提取的长期偏好，返回空数组。\n"
                    "你必须只返回 JSON，格式固定为："
                    '{{"memories":[{{"type":"budget_preference","content":"预算 3000 元以内"}}]}}\n'
                    '如果没有可提取内容，则返回：{{"memories":[]}}'
                ),
                (
                    "user",
                    "请从下面的对话中提取长期有用的租房偏好记忆。\n"
                    "用户消息：{user_message}\n"
                    "AI 回复：{answer}"
                ),
            ]
        )


def build_rental_memory_extract_prompt() -> ChatPromptTemplate:
    return RentalMemoryExtractPrompt.build()
