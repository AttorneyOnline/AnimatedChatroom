import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Type

import msgpack
import struct
import hashlib
from network import packets


class ClientHandler:

    def __init__(self, client):
        self.client = client

    def respond(self, msg: packets.Packet):
        self.client.write(msg)

    def handle_message(self, msg):
        try:
            getattr(self, msg['id'])(msg)
        except AttributeError:
            pass

    def handle_connect(self):
        pass

    def handle_disconnect(self):
        pass

    def handle_exception(self, exc: Exception):
        pass


class Client:

    def __init__(self, address, port='42505'):
        self.address = address
        self.port = port

        # A general handler. Useful for handling messages that we did not expect.
        self.handler = None

        # Populated only after a connection has been established.
        self._transport = None
        self._protocol = None

        # Populated only when a server info request is made.
        self.server_info = None

        # This challenge/nonce is reused across the entire session.
        self.challenge = None
        self.rooms = None

        # loop hooks on once the connection is established. The client may be instantiated
        # on one thread but then the connect may be called on another one.
        self.loop = None

    async def connect(self, disconnect_future: asyncio.Future = None):
        self.loop = asyncio.get_event_loop()
        try:
            self._transport, self._protocol = \
                await self.loop.create_connection(lambda: ClientProtocol(self, disconnect_future),
                                             self.address, self.port)
        except OSError:
            disconnect_future.cancel()
            raise

    def handle_message(self, packet: dict):
        try:
            self.handler.handle_message(packet)
        except KeyError:
            pass

    def handle_connect(self):
        try:
            self.handler.handle_connect()
        except KeyError:
            pass

    def write(self, msg: packets.Packet):
        self._protocol.write(msg)

    def send_request(self, future: asyncio.Future,
                     msg: packets.Packet, expected_response: Type[packets.Packet]):
        self._protocol.send_request(future, msg, expected_response)

    def close(self):
        if self._transport is not None and not self._transport.is_closing():
            self.write(packets.Goodbye())
            self._transport.close()
        try:
            self.handler.handle_disconnect()
        except KeyError:
            pass

    async def get_server_info(self):
        future = asyncio.Future()
        self.send_request(future,
                          packets.ServerInfoRequest(packets.ServerInfoRequest.ServerInfoRequestType.FULL),
                          packets.ServerInfoResponse)
        result = await future
        self.challenge = result['auth_challenge']
        return result

    async def join_server(self, name: str, password: str = None):
        self.player_name = name
        sha256 = hashlib.sha256()
        if password is not None:
            sha256.update(password.encode("utf-8"))
        sha256.update(self.challenge)
        future = asyncio.Future()
        self.send_request(future, packets.JoinRequest(name, sha256.digest()), packets.JoinResponse)
        result = await future
        # Parse response
        result_codes = packets.JoinResponse.JoinResult
        if result['result_code'] == result_codes.SUCCESS:
            return result
        elif result['result_code'] == result_codes.SERVER_FULL:
            raise ConnectionError("The server is full.")
        elif result['result_code'] == result_codes.BAD_PASSWORD:
            raise ConnectionError("The password was incorrect.")
        elif result['result_code'] == result_codes.BANNED:
            raise ConnectionError("You are banned.\nReason: {}".format(result['result_msg']))
        elif result['result_code'] == result_codes.OTHER:
            raise ConnectionError("You cannot join for the following reason:\n{}".format(result['result_msg']))
        else:
            raise ConnectionError("The join result was not understood: {}".format(result['result_code']))

    async def get_rooms(self):
        """
        Doesn't exist.
        """
        future = asyncio.Future()
        self.send_request(future, packets.RoomListRequest(), packets.RoomListResponse)
        return await future

    async def join_room(self, room_id: int, password: str = None):
        future = asyncio.Future()
        auth_response = None
        if password is not None:
            sha256 = hashlib.sha256()
            sha256.update(password.encode("utf-8"))
            sha256.update(self.challenge)
            auth_response = sha256.digest()
        self.send_request(future, packets.JoinRoomRequest(room_id, auth_response), packets.JoinRoomResponse)
        return await future


class MockClientHandler(ClientHandler):
    pass


class ClientProtocol(asyncio.Protocol):

    def __init__(self, client, disconnect_future: asyncio.Future = None):
        super().__init__()
        self._client = client
        self._buffer = None
        # Maps packet IDs to futures
        self._futures = dict()
        self._disconnect_future = disconnect_future

    def write(self, message: packets.Packet):
        if self.transport.is_closing():
            raise ConnectionError("Connection is already closed")
        self.transport.write(message.encode())

    def send_request(self, future: asyncio.Future,
                     message: packets.Packet, expected_response: Type[packets.Packet]):
        self.write(message)
        if expected_response.msgid not in self._futures:
            self._futures[expected_response.msgid] = []
        self._futures[expected_response.msgid].append(future)

    def connection_made(self, transport: asyncio.Transport):
        self.transport = transport

    def connection_lost(self, exc: Exception):
        print("Connection lost:", exc)
        for futures in self._futures.values():
            for future in futures:
                future.cancel()
        if self._disconnect_future is not None:
            self._disconnect_future.set_result(exc)

    def data_received(self, data: bytes):
        # Put it in a buffer and wait until it's filled
        if self._buffer is not None:
            self._buffer += data
        else:
            self._buffer = bytearray(data)
        if len(self._buffer) == 0:
            return
        msg_size = struct.unpack_from("<I", self._buffer)[0]
        # First four bytes of a message contain the length (uint32 little-endian).
        if len(self._buffer) >= msg_size + 4:
            # Handle the packet
            msg = msgpack.unpackb(self._buffer[4:msg_size + 4], encoding='utf-8')
            print(msg)
            try:
                # Fulfill all futures that are waiting on this packet
                if msg['id'] in self._futures:
                    for future in self._futures[msg['id']]:
                        future.set_result(msg)
                    del self._futures[msg['id']]
                # Call general message handler
                loop = asyncio.get_event_loop()
                loop.call_soon_threadsafe(self._client.handle_message, msg)
            except KeyError:
                print("Unknown packet!")
            # Handle the other part of the packet (there might be two messages
            # wedged into one packet)
            remaining = self._buffer[msg_size + 4:]
            self._buffer = None
            self.data_received(remaining)

if __name__ == '__main__':
    #import binascii
    #with open("R:/hope", "w") as f:
    #    f.write(binascii.hexlify(packets.ServerInfoRequest(packets.ServerInfoRequest.ServerInfoRequestType.BASIC).encode()).decode("utf-8"))
    #with open("R:/hope2", "w") as f:
    #    f.write(binascii.hexlify(packets.JoinRequest("topokeke", None).encode()).decode("utf-8"))
    loop = asyncio.get_event_loop()
    client = Client('75.1.215.23', port='42505')
    handler = MockClientHandler(client)
    client.handler = handler
    async def test():
        await client.connect()
        info = await client.get_server_info()
        await client.join_server("longboi", "abcd")
        print(info['rooms'])
        await client.join_room(1, "abcd")
        client.close()
    test_task = loop.create_task(test())
    loop.run_until_complete(test_task)
