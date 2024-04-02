from langchain.prompts.chat import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from memory.buffer_redis import RedisBufferWindowChatMessageHistory


from . import templ

def get_chat_chain(model, redis_url, buffer_size, ttl):
    messages = [
        SystemMessagePromptTemplate.from_template(templ.SYSTEM_TEMPLATE),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ]

    prompt = ChatPromptTemplate.from_messages(messages)
    output_parser = StrOutputParser()
    base_chain = prompt | model | output_parser
    chain = RunnableWithMessageHistory(
    base_chain,
    lambda session_id: RedisBufferWindowChatMessageHistory(
            session_id,
            url=redis_url,
            buffer_size=buffer_size,
            ttl=ttl,
        ),
        input_messages_key="input",
        history_messages_key="chat_history",
    )
    return chain
