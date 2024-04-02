from langchain.schema import BaseMemory
from langchain_core.language_models import BaseChatModel
from langchain.globals import set_verbose
import re
import logging


from typing import Optional

from langchain_core.prompts import SystemMessagePromptTemplate, MessagesPlaceholder

from chains.chat import templ
from chains.chat.base import get_chat_chain
from memory.buffer_redis import RedisBufferWindowChatMessageHistory

set_verbose(True)

class ChatWorkflow():
    model: BaseChatModel
    redis_url: str
    ttl: Optional[int]
    buffer_size: int

    def __init__(self, model,  history_buffer_size, redis_url, ttl: Optional[int] = None):
        self.model = model
        self.redis_url = redis_url
        self.ttl = ttl
        self.buffer_size = history_buffer_size

    def invoke(self, inputs: dict):
        chat_chain = get_chat_chain(self.model, self.redis_url, self.buffer_size, self.ttl)
        config = {"configurable": {"session_id": inputs["session_id"]}}
        raw_resp = chat_chain.invoke({"input": inputs["input"], "character_name": inputs["character_name"], "character_description": inputs["character_description"]}, config=config)
        return extract_quotes(raw_resp)
    def stream(self, inputs: dict):
        chat_chain = get_chat_chain(self.model, self.redis_url, self.buffer_size, self.ttl)
        config = {"configurable": {"session_id": inputs["session_id"]}}
        try:
            for chunk in chat_chain.stream({"input": inputs["input"], "character_name": inputs["character_name"],"character_description": inputs["character_description"]}, config=config):
                yield chunk
        except Exception as e:
            logging.error(f"chat chain stream error: {e}")
            yield {"error": e}
            return

def extract_quotes(input_string):
    matches = re.findall(r'"([^"]*)"', input_string)
    if matches:
        return matches[0]
    else:
        return input_string


