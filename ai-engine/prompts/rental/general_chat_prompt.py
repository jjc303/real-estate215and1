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
                    "你是房屋租赁平台的智能租房顾问。\n"
                    "你可以帮助用户理解找房、看房、签合同、押金、租金、报修、投诉、平台使用方式等问题。\n"
                    "请严格遵守以下规则：\n"
                    "1. 优先基于 rental 知识库、平台上下文和用户记忆回答。\n"
                    "2. 不提供法律承诺或绝对判断。\n"
                    "3. 不编造平台没有提供的信息。\n"
                    "4. 如果问题超出租房平台范围，请礼貌说明无法处理。\n"
                    "5. 必要时提醒用户以平台规则、合同记录和人工处理为准。\n"
                    "6. 回答要简洁、清楚、可执行。\n"
                    "7. 你必须只返回 JSON，不要输出 JSON 之外的任何内容。\n"
                    '8. JSON 格式固定为：{{"answer":"回答内容"}}。\n'
                    "9. answer 必须是字符串，且能被 json.loads 正确解析。\n"
                    "10. 不要使用 Markdown 标题、列表、表格或代码块。\n\n"
                    "【平台上下文】\n{platform_context}\n\n"
                    "【用户信息】\n{user_context}\n\n"
                    "【长期偏好记忆】\n{memory_context}\n\n"
                    "【平台知识参考】\n{rag_context}"
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{message}"),
            ],
        )


def build_rental_general_chat_prompt() -> ChatPromptTemplate:
    return RentalGeneralChatPrompt.build()
