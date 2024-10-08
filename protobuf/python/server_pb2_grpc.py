# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import protobuf.python.server_pb2 as server__pb2


class AgentStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Chat = channel.unary_unary(
                '/starland_chat_agent.Agent/Chat',
                request_serializer=server__pb2.ChatRequest.SerializeToString,
                response_deserializer=server__pb2.ChatResponse.FromString,
                )
        self.ChatStream = channel.unary_stream(
                '/starland_chat_agent.Agent/ChatStream',
                request_serializer=server__pb2.ChatRequest.SerializeToString,
                response_deserializer=server__pb2.ChatStreamResponse.FromString,
                )


class AgentServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Chat(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ChatStream(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_AgentServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Chat': grpc.unary_unary_rpc_method_handler(
                    servicer.Chat,
                    request_deserializer=server__pb2.ChatRequest.FromString,
                    response_serializer=server__pb2.ChatResponse.SerializeToString,
            ),
            'ChatStream': grpc.unary_stream_rpc_method_handler(
                    servicer.ChatStream,
                    request_deserializer=server__pb2.ChatRequest.FromString,
                    response_serializer=server__pb2.ChatStreamResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'starland_chat_agent.Agent', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Agent(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Chat(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/starland_chat_agent.Agent/Chat',
            server__pb2.ChatRequest.SerializeToString,
            server__pb2.ChatResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def ChatStream(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/starland_chat_agent.Agent/ChatStream',
            server__pb2.ChatRequest.SerializeToString,
            server__pb2.ChatStreamResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
