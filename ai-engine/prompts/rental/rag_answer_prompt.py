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
                    "你是房屋租赁平台的知识助手。\n"
                    "你只能使用 rental 知识库和平台上下文来辅助回答租房问题。\n"
                    "有检索结果时，请结合检索内容作答；没有检索结果时，可以基于一般租房常识给出保守回答。\n"
                    "不要编造具体平台规则，不要编造政策、法律结论或合同效力。必要时提醒用户以平台规则、合同记录和人工处理为准。\n"
                    '你必须只返回 JSON，格式固定为：{{"answer":"回答内容"}}'
                ),
                ("user", "用户问题：{message}\n\n知识库片段：\n{rag_context}"),
            ]
        )


def build_rental_rag_answer_prompt() -> ChatPromptTemplate:
    return RentalRAGAnswerPrompt.build()
