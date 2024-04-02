from typing import Any, AsyncIterator, Dict, Iterator, List, Optional

from langchain_core.callbacks import (
    AsyncCallbackManagerForLLMRun,
    CallbackManagerForLLMRun,
)
from langchain_core.language_models import BaseChatModel, SimpleChatModel
from langchain_core.messages import AIMessageChunk, BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult
from langchain_core.runnables import run_in_executor
from langchain_core.language_models.chat_models import agenerate_from_stream

import json, requests, redis, uuid
import aioredis


class RedisTaskYi34BChat(BaseChatModel):
    redis_url: str
    redis_client: redis.Redis
    task_queue_key: str
    temperature: float = 0.0
    model_params: dict = None

    @staticmethod
    def from_url(redis_url: str, task_queue_key: str, temperature: float = 0.0, model_params: dict = None):
        return RedisTaskYi34BChat(
            redis_url=redis_url,
            redis_client=redis.Redis.from_url(redis_url),
            task_queue_key=task_queue_key,
            temperature=temperature,
            model_params=model_params)

    @property
    def _llm_type(self) -> str:
        """Get the type of language model used by this chat model."""
        return "redis-task-yi-34b-chat"

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Return a dictionary of identifying parameters."""
        return {"task_queue_key": self.task_queue_key, "temperature": self.temperature}

    def _generate(
            self,
            messages: List[BaseMessage],
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> ChatResult:
        temperature = kwargs.get("temperature") if kwargs.get("temperature") is not None else self.temperature
        task_id = str(uuid.uuid4())

        task_messages = []
        for msg in messages:
            if isinstance(msg, SystemMessage):
                task_messages.append({"role": "system", "content": msg.content})
            elif isinstance(msg, HumanMessage):
                task_messages.append({"role": "human", "content": msg.content})
            elif isinstance(msg, AIMessage):
                task_messages.append({"role": "ai", "content": msg.content})

        # print(f"chat redis model, task_messages: {task_messages}")
        task = {"task_id": task_id, "prompt": "", "history": [], "temperature": temperature, "messages": task_messages}
        if "model_params" in kwargs:
            task["model_params"] = kwargs["model_params"]
        elif self.model_params is not None:
            task["model_params"] = self.model_params
        self.redis_client.lpush(self.task_queue_key, json.dumps(task))
        output = self.redis_client.brpop(task_id)[1].decode("utf-8")

        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=output))])

    def _stream(
            self,
            messages: List[BaseMessage],
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        temperature = kwargs.get("temperature") if kwargs.get("temperature") is not None else self.temperature
        task_id = str(uuid.uuid4())

        task_messages = []
        for msg in messages:
            if isinstance(msg, SystemMessage):
                task_messages.append({"role": "system", "content": msg.content})
            elif isinstance(msg, HumanMessage):
                task_messages.append({"role": "human", "content": msg.content})
            elif isinstance(msg, AIMessage):
                task_messages.append({"role": "ai", "content": msg.content})

        task = {"task_id": task_id, "prompt": "", "history": [], "temperature": temperature, "messages": task_messages,
                "stream": True}
        if "model_params" in kwargs:
            task["model_params"] = kwargs["model_params"]
        elif self.model_params is not None:
            task["model_params"] = self.model_params

        self.redis_client.lpush(self.task_queue_key, json.dumps(task))
        while True:
            chunk = self.redis_client.brpop(task_id)
            print(f"receive chunk from redis {chunk}")
            chunk = json.loads(chunk[1])

            response_metadata = chunk["data"]["response_metadata"]
            finish_reason = response_metadata.get("finish_reason")
            generation_info = (
                dict(finish_reason=finish_reason) if finish_reason is not None else response_metadata
            )
            chunk = ChatGenerationChunk(message=AIMessageChunk(**chunk["data"]), generation_info=generation_info)
            yield chunk

            if run_manager:
                run_manager.on_llm_new_token(token=chunk.text, chunk=chunk)

            if finish_reason is not None or response_metadata:
                break

    async def _astream(
            self,
            messages: List[BaseMessage],
            stop: Optional[List[str]] = None,
            run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> AsyncIterator[ChatGenerationChunk]:
        temperature = kwargs.get("temperature") if kwargs.get("temperature") is not None else self.temperature
        task_id = str(uuid.uuid4())

        task_messages = []
        for msg in messages:
            if isinstance(msg, SystemMessage):
                task_messages.append({"role": "system", "content": msg.content})
            elif isinstance(msg, HumanMessage):
                task_messages.append({"role": "human", "content": msg.content})
            elif isinstance(msg, AIMessage):
                task_messages.append({"role": "ai", "content": msg.content})

        # print(f"chat redis model, task_messages: {task_messages}")
        task = {"task_id": task_id, "prompt": "", "history": [], "temperature": temperature, "messages": task_messages,
                "stream": True}
        if "model_params" in kwargs:
            task["model_params"] = kwargs["model_params"]
        elif self.model_params is not None:
            task["model_params"] = self.model_params

        aredis_client = aioredis.from_url(self.redis_url)
        await aredis_client.lpush(self.task_queue_key, json.dumps(task))
        while True:
            chunk = await aredis_client.brpop(task_id)
            # print(chunk)
            chunk = json.loads(chunk[1])
            finish_reason = chunk["data"]["response_metadata"].get("finish_reason")
            generation_info = (
                dict(finish_reason=finish_reason) if finish_reason is not None else None
            )
            chunk = ChatGenerationChunk(message=AIMessageChunk(**chunk["data"]), generation_info=generation_info)
            yield chunk

            if run_manager:
                await run_manager.on_llm_new_token(token=chunk.text, chunk=chunk)

            if finish_reason is not None:
                break

    async def _agenerate(
            self,
            messages: List[BaseMessage],
            stop: Optional[List[str]] = None,
            run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
            stream: Optional[bool] = None,
            **kwargs: Any,
    ) -> ChatResult:
        should_stream = stream if stream is not None else self.streaming
        if should_stream:
            stream_iter = self._astream(
                messages, stop=stop, run_manager=run_manager, **kwargs
            )
            return await agenerate_from_stream(stream_iter)

        return await run_in_executor(
            None,
            self._generate,
            messages,
            stop,
            run_manager.get_sync() if run_manager else None,
            **kwargs,
        )


