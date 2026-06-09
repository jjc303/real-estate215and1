"""Prompt for answering with rental RAG context."""

from langchain_core.prompts import ChatPromptTemplate


class RentalRAGAnswerPrompt:
    """Build prompt for rental RAG grounded answers."""

    @staticmethod
    def build() -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "你是房屋租赁平台的知识助手，基于知识库回答用户的租房问题。\n\n"
                    "如果有知识库内容，请结合检索结果回答；如果没有，可以基于租房常识给出参考建议。\n"
                    "语气自然，像有经验的房产顾问一样聊天。\n"
                    "涉及合同、押金等需要谨慎的问题时，提醒用户以平台记录和合同文本为准。\n\n"
                    "【输出格式】\n"
                    '你最后必须输出 JSON 格式：{{"answer":"你的回答"}}'
                ),
                ("user", "用户问题：{message}\n\n知识库片段：\n{rag_context}"),
            ]
        )


def build_rental_rag_answer_prompt() -> ChatPromptTemplate:
    return RentalRAGAnswerPrompt.build()
