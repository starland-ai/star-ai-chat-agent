from langchain.memory import RedisChatMessageHistory, ConversationBufferMemory, CombinedMemory, RedisEntityStore
from langchain_core.messages import BaseMessage, message_to_dict


from typing import List, Optional, Dict, Any
import json
import logging

class RedisBufferWindowChatMessageHistory(RedisChatMessageHistory):
    buffer_size : int

    def __init__(
        self,
        session_id: str,
        url: str = "redis://localhost:6379/0",
        key_prefix: str = "message_store:",
        ttl: Optional[int] = None,
        buffer_size: int = 20,
    ):
        RedisChatMessageHistory.__init__(self, session_id=session_id, url=url, key_prefix=key_prefix, ttl=ttl)
        self.buffer_size = buffer_size

    def add_message(self, message: BaseMessage) -> None:
        """Append the message to the record in Redis"""
        logging.debug(f"adding message {message} to redis")
        logging.debug(f"message to dict: {message_to_dict(message)}")
        self.redis_client.lpush(self.key, json.dumps(message_to_dict(message)))
        size = self.redis_client.llen(self.key)
        if size > self.buffer_size:
            self.redis_client.ltrim(self.key, 0, self.buffer_size - 1)
        if self.ttl:
            self.redis_client.expire(self.key, self.ttl)
