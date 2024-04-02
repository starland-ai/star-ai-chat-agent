import logging
import langchain
import yaml
import redis
import grpc

from chat_workflow import ChatWorkflow
from db.models import init_models
from models.redis import RedisTaskYi34BChat
from concurrent import futures

from service import ChatAgentService
import protobuf.python.server_pb2_grpc as server_pb2_grpc

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S',)
    logging.getLogger('urllib3.connectionpool').setLevel(logging.CRITICAL)
    logging.getLogger('openai').setLevel(logging.CRITICAL)
    logging.getLogger('langchain.vectorstores.milvus').setLevel(logging.CRITICAL)
    logging.getLogger('urllib3.util.retry').setLevel(logging.CRITICAL)
    langchain.verbose = True

    yaml_file = "config/config.yaml"
    with open(yaml_file, 'r') as f:
        cfg = yaml.safe_load(f)

    init_models(cfg["mysql_host"], cfg["mysql_user"], cfg["mysql_passwd"], cfg["mysql_db"])

    model = RedisTaskYi34BChat.from_url(redis_url=cfg["redis_url"], temperature=cfg["default_temperature"], task_queue_key=cfg["redis_task_key"])
    workflow = ChatWorkflow(model,cfg["history_buffer_size"],cfg["redis_url"],cfg["history_ttl"])

    options = [('grpc.max_send_message_length', 1024 * 1024 * 1024),
               ('grpc.max_receive_message_length', 1024 * 1024 * 1024), ('grpc.max_metadata_size', 1024 * 1024)]
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2000), options=options)

    servicer = ChatAgentService(workflow=workflow)
    server_pb2_grpc.add_AgentServicer_to_server(servicer, server)

    server.add_insecure_port(f'[::]:{cfg["listen_port"]}')
    server.start()
    logging.info(f'listen on {cfg["listen_port"]}')
    server.wait_for_termination()

