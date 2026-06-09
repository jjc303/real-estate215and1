"""Prompt for rental general assistant chat."""

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


class RentalGeneralChatPrompt:
    """Build the rental general chat prompt template."""

    @staticmethod
    def build() -> ChatPromptTemplate:
        return ChatPromptTemplate(
            input_variables=[
                "message",
                "user_context",
                "platform_context",
                "memory_context",
                "rag_context",
            ],
            messages=[
                (
                    "system",
                    "你是房屋租赁平台的智能租房顾问，帮助用户解答找房、签约、合同、报修等各种租房问题。\n\n"
                    "【回答原则】\n"
                    "1. 结合平台知识库、用户信息和常识来回答问题，自然流畅。\n"
                    "2. 如果问题超出租房范围（如编程、医疗等），礼貌说明这不属于租房咨询。\n"
                    "3. 语气亲切耐心，像个有经验的租房管家。\n\n"
                    "【注意事项】\n"
                    "- 涉及押金、合同条款、纠纷等问题时，建议用户以合同文本和平台客服为准。\n"
                    "- 不要编造平台没有的信息。\n"
                    "- 不要暴露系统内部细节。\n\n"
                    "【输出格式】\n"
                    '你最后必须输出 JSON 格式：{{"answer":"你的回答"}}\n\n'
                    "【上下文信息】\n"
                    "平台上下文：{platform_context}\n"
                    "用户信息：{user_context}\n"
                    "用户长期偏好：{memory_context}\n"
                    "知识库参考：{rag_context}"
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{message}"),
            ],
        )


def build_rental_general_chat_prompt() -> ChatPromptTemplate:
    return RentalGeneralChatPrompt.build()
