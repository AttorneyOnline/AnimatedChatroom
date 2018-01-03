import asyncio
import msgpack
import struct
import hashlib
from network import packets


class Client:

    def __init__(self, loader, address, port='42505'):
        self.address = address
        self.port = port
        self.loader = loader
        loop = asyncio.get_event_loop()
        self.transport = loop.create_connection(lambda: ClientProtocol(self), address, port)
        self.loader.status = "Connecting to client..."
        self.loader.progress = 0
        #loop.run_until_complete(self.transport)

class ClientProtocol(asyncio.Protocol):

    def __init__(self, client):
        super().__init__()
        self.client = client
        self.buffer = None

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
            self.buffer = self.buffer[msg_size+4:]
            print(msg)
            try:
                self.handler_table[msg['id']](self, msg)
            except KeyError:
                print("Unknown packet!")

    def handle_server_info_response(self, packet: dict):
        self.client.loader.status = "Joining server..."
        self.client.loader.progress = 20
        self.challenge = packet['auth_challenge']
        sha256 = hashlib.sha256()
        sha256.update("abcd".encode("utf-8"))
        sha256.update(self.challenge)
        self.transport.write(packets.JoinRequest("longboi", sha256.digest()).encode())
        #asyncio.get_event_loop().call_soon_threadsafe(self.join_room, 1)
        #self.handle_join_response(packet)
        #self.transport.write(packets.AssetListRequest().encode())

    def handle_join_response(self, packet: dict):
        self.client.loader.status = "Complete"
        self.client.loader.progress = 100
        self.client.loader.done()
        pass

    def join_room(self, room_no: int):
        sha256 = hashlib.sha256()
        sha256.update("abcd".encode("utf-8"))
        sha256.update(self.challenge)
        self.transport.write(packets.JoinRoomRequest(room_no, sha256.digest()).encode())

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

if __name__ == '__main__':
    #import binascii
    #with open("R:/hope", "w") as f:
    #    f.write(binascii.hexlify(packets.ServerInfoRequest(packets.ServerInfoRequest.ServerInfoRequestType.BASIC).encode()).decode("utf-8"))
    #with open("R:/hope2", "w") as f:
    #    f.write(binascii.hexlify(packets.JoinRequest("topokeke", None).encode()).decode("utf-8"))
    client = Client('75.1.215.23', port='42505')
    asyncio.get_event_loop().run_forever()
    asyncio.get_event_loop().close()