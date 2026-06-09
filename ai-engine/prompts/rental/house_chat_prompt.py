"""Prompt for rental house-specific chat."""

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


class RentalHouseChatPrompt:
    """Build the rental house chat prompt template."""

    @staticmethod
    def build() -> ChatPromptTemplate:
        return ChatPromptTemplate(
            input_variables=[
                "message",
                "house_context",
                "user_context",
                "platform_context",
                "memory_context",
                "rag_context",
            ],
            messages=[
                (
                    "system",
                    "你是房屋租赁平台的智能租房助手。\n"
                    "你正在回答用户关于当前房源的问题，语气要自然友好，像个房产顾问一样。\n\n"
                    "回答原则：\n"
                    "1. 优先基于平台提供的房源信息（house_context）回答。\n"
                    "2. 如果房源信息里没有用户问的内容，可以结合常识给出参考建议。\n"
                    "3. 涉及押金、合同条款等问题时，提醒用户以合同文本和平台客服为准。\n"
                    "4. 不要编造具体的房东联系方式、优惠活动或平台未提供的承诺。\n"
                    "5. 不要暴露系统内部细节。\n\n"
                    "输出格式：\n"
                    '最后必须输出 JSON：{{"answer":"你的回答"}}\n\n'
                    "上下文信息：\n"
                    "平台上下文：{platform_context}\n"
                    "用户信息：{user_context}\n"
                    "房源信息：{house_context}\n"
                    "用户长期偏好：{memory_context}\n"
                    "知识库参考：{rag_context}"
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{message}"),
            ],
        )


def build_rental_house_chat_prompt() -> ChatPromptTemplate:
    return RentalHouseChatPrompt.build()
