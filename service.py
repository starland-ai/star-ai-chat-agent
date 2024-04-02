import logging

import protobuf.python.server_pb2 as server_pb2
import protobuf.python.server_pb2_grpc as server_pb2_grpc
from chat_workflow import ChatWorkflow
from db.models import get_character_name, get_character_prompt


class ChatAgentService(server_pb2_grpc.AgentServicer):
    workflow: ChatWorkflow

    def __init__(self, workflow):
        super().__init__()
        self.workflow = workflow

    def Chat(self, request, context):
        logging.info(f"recevie request: {request}")
        character_id = request.character_id
        session_id = request.conversation_id
        input = request.message.decode('utf-8')
        character_name = get_character_name(character_id)
        character_desc = get_character_prompt(character_id)

        logging.debug(f"conversation:{session_id}, character: {character_name}, receive chat message: {input}")
        inputs = {"session_id": session_id, "input": input, "character_name": character_name, "character_description": character_desc}

        resp = self.workflow.invoke(inputs)
        logging.info(f"invoke response is: {resp}")
        return server_pb2.ChatResponse(code=0, err_msg="", response_text=resp)


    def ChatStream(self, request, context):
        logging.info(f"recevie request: {request}")
        character_id = request.character_id
        session_id = request.conversation_id
        input = request.message.decode('utf-8')
        character_name = get_character_name(character_id)
        character_desc = get_character_prompt(character_id)

        logging.debug(f"conversation:{session_id}, character: {character_name}, receive chat message: {input}")
        inputs = {"session_id": session_id, "input": input, "character_name": character_name,
                  "character_description": character_desc}
        for chunk in self.workflow.stream(inputs):
            logging.info(f"chunk is: {chunk}")
            if "error" in chunk:
                yield server_pb2.ChatStreamResponse(code=1, err_msg=f"{chunk['error']}")
            yield server_pb2.ChatStreamResponse(code=0, err_msg="", chunk=chunk)
