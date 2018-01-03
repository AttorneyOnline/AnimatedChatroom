import asyncio
from concurrent.futures import ThreadPoolExecutor

import msgpack
import struct
import hashlib
from network import packets


class ClientHandler:

    def __init__(self, client):
        self.client = client

    def respond(self, msg: packets.Packet):
        self.client._transport.write(msg)

    def handle_message(self, msg):
        self.handler_table[msg['id']](self, msg)

    def handle_exception(self, exc: Exception):
        pass

    def handle_server_info_response(self, packet: dict):
        pass

    def handle_join_response(self, packet: dict):
        pass

    def handle_asset_list_response(self, packet: dict):
        pass

    def handle_goodbye_packet(self, packet: dict):
        print("disconnect")

    def handle_join_room_response(self, packet: dict):
        pass

    handler_table = {
        packets.ServerInfoResponse.msgid: handle_server_info_response,
        packets.JoinResponse.msgid: handle_join_response,
        packets.Goodbye.msgid: handle_goodbye_packet,
        packets.AssetListResponse.msgid: handle_asset_list_response,
        packets.JoinRoomResponse.msgid: handle_join_room_response
    }


class Client:

    def __init__(self, address, port='42505'):
        self.address = address
        self.port = port
        self.handler = None
        self._transport = None
        self.challenge = None

    def connect(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._connect())

    async def _connect(self):
        loop = asyncio.get_event_loop()
        self._transport = await loop.create_connection(lambda: ClientProtocol(self), self.address, self.port)

    def join_room(self, room_no: int):
        raise NotImplementedError


class MockClientHandler(ClientHandler):

    def handle_server_info_response(self, packet: dict):
        self.challenge = packet['auth_challenge']
        sha256 = hashlib.sha256()
        sha256.update("abcd".encode("utf-8"))
        sha256.update(self.challenge)
        self.respond(packets.JoinRequest("longboi", sha256.digest()))

    def handle_join_response(self, packet: dict):
        pass

    def join_room(self, room_no: int):
        sha256 = hashlib.sha256()
        sha256.update("abcd".encode("utf-8"))
        sha256.update(self.challenge)
        self.respond(packets.JoinRoomRequest(room_no, sha256.digest()))

    def handle_goodbye_packet(self, packet: dict):
        print("disconnect")


class ClientProtocol(asyncio.Protocol):

    def __init__(self, client):
        super().__init__()
        self.client = client
        self.buffer = None

    def write(self, message: packets.Packet):
        self.transport.write(message.encode())

    def connection_made(self, transport: asyncio.Transport):
        self.transport = transport
        transport.write(packets.ServerInfoRequest(packets.ServerInfoRequest.ServerInfoRequestType.FULL).encode())

    def connection_lost(self, exc: Exception):
        print("Connection lost:", exc)

    def data_received(self, data: bytes):
        # Put it in a buffer and wait until it's filled
        if self.buffer is not None:
            self.buffer += data
        else:
            self.buffer = bytearray(data)
        msg_size = struct.unpack_from("<I", self.buffer)[0]
        # First four bytes of a message contain the length (uint32 little-endian).
        if len(self.buffer) >= msg_size + 4:
            # Handle the packet
            msg = msgpack.unpackb(self.buffer[4:msg_size+4], encoding='utf-8')
            print(msg)
            try:
                loop = asyncio.get_event_loop()
                loop.call_soon_threadsafe(self.client.handle_message, self, msg)
            except KeyError:
                print("Unknown packet!")
            # Handle the other part of the packet (there might be two messages
            # wedged into one packet)
            remaining = self.buffer[msg_size+4:]
            self.buffer = None
            self.data_received(remaining)

if __name__ == '__main__':
    #import binascii
    #with open("R:/hope", "w") as f:
    #    f.write(binascii.hexlify(packets.ServerInfoRequest(packets.ServerInfoRequest.ServerInfoRequestType.BASIC).encode()).decode("utf-8"))
    #with open("R:/hope2", "w") as f:
    #    f.write(binascii.hexlify(packets.JoinRequest("topokeke", None).encode()).decode("utf-8"))
    client = Client('75.1.215.23', MockClientHandler, port='42505')
    client.connect()