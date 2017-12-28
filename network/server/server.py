import asyncio
import msgpack

class Server:

    def __init__(self, address='0.0.0.0', port=27017):
        self.address = address
        self.port = port
        self.clients = []
        loop = asyncio.get_event_loop()
        self.server = loop.create_server(Protocol(self), address, port)


class Protocol(asyncio.Protocol):

    def __init__(self, server: Server):
        super().__init__()
        self.server = server
        self.client = None

    def connection_made(self, transport: asyncio.Transport):
        """
        Called on connection. By default, we wait a few seconds for the
        client to say something before we drop it off (background
        Internet traffic).
        """
        self.drop_timer = asyncio.get_event_loop().call_later(4, self.drop_client)

    def connection_lost(self, exc: Exception):
        """
        Called on connection loss.
        """
        self.drop_client()

    def drop_client(self):
        if self.client is not None:
            self.server.clients.remove(self.client)

    def data_received(self, data: bytes):
        msg = msgpack.unpackb(data, encoding='utf-8')
        if msg['id'] == 'ServerInfoRequest':
            if self.drop_timer is not None:
                self.drop_timer.cancel()
        # The rest follows...