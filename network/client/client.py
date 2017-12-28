import asyncio
import msgpack
from .. import packets


class Client:

    def __init__(self, address, port='27017'):
        self.address = address
        self.port = port
        loop = asyncio.get_event_loop()
        self.transport = loop.create_connection(lambda: ClientProtocol(self), address, port)


class ClientProtocol(asyncio.Protocol):

    def __init__(self, client):
        super().__init__()
        self.client = client

    def connection_made(self, transport: asyncio.Transport):
        transport.write(packets.ServerInfoRequest(packets.ServerInfoRequest.ServerInfoRequestType.BASIC).encode())

    def connection_lost(self, exc: Exception):
        pass

    def data_received(self, data: bytes):
        msg = msgpack.unpackb(data, encoding='utf-8')
        self.handler_table[msg['id']](msg)

    def handle_server_info_response(self, packet: dict):
        pass

    def handle_join_response(self, packet: dict):
        pass

    def handle_asset_list_response(self, packet: dict):
        pass

    handler_table = {
        packets.ServerInfoResponse.id: handle_server_info_response,
        packets.JoinResponse.id: handle_join_response
    }
