"""
Contains all network packets.
"""
from enum import Enum
import msgpack


class Packet:
    msgid = None

    def encode(self):
        """Encode the message using msgpack."""
        print("writing:", self.__dict__)
        return msgpack.packb(self.__dict__, use_bin_type=True)


class ServerInfoRequest(Packet):
    class ServerInfoRequestType:
        PING = 0
        BASIC = 1
        FULL = 2

    msgid = 'ServerInfoRequest'

    def __init__(self, request_type: ServerInfoRequestType):
        self.id = self.msgid
        self.type = request_type


class ServerInfoResponse(Packet):
    class Protection:
        OPEN = 0
        JOIN_WITH_PASSWORD = 1
        SPECTATE_ONLY = 2
        WHITELIST = 3
        CLOSED = 4

    class Details:
        def __init__(self, auth_challenge: bytes, desc: str, players: list):
            self.auth_challenge = auth_challenge
            self.desc = desc
            self.players = players

    msgid = 'ServerInfoResponse'

    def __init__(self, name: str, address: str, port: int, version: str, player_count: int,
                 max_players: int, protection: int, details: Details):
        self.name = name
        self.address = address
        self.port = port
        self.version = version
        self.player_count = player_count
        self.max_players = max_players
        self.protection = protection
        self.details = details


class JoinRequest(Packet):
    msgid = 'JoinRequest'

    def __init__(self, *, player_name: str, player_id: str, auth_response: bytes = None, master: bool = True):
        self.id = self.msgid
        self.player_id = player_id
        self.player_name = player_name
        self.auth_response = auth_response
        self.master = master


class JoinResponse(Packet):
    class JoinResult:
        SUCCESS = 0
        SERVER_FULL = 1
        BAD_PASSWORD = 2
        BANNED = 3
        OTHER = 4

    msgid = 'JoinResponse'

    def __init__(self, result: JoinResult, msg: str):
        self.id = self.msgid
        self.result = result
        self.msg = msg


class RoomListRequest(Packet):
    msgid = 'RoomListRequest'

    def __init__(self):
        self.id = self.msgid

class RoomListResponse(Packet):
    msgid = 'RoomListResponse'


class JoinRoomRequest(Packet):
    msgid = 'JoinRoomRequest'

    def __init__(self, room_id: int, auth_response: bytes = None):
        self.id = self.msgid
        self.room_id = room_id
        self.auth_response = auth_response


class JoinRoomResponse(Packet):
    class JoinRoomResult:
        SUCCESS = 0
        ROOM_FULL = 1
        BAD_PASSWORD = 2

    msgid = 'JoinRoomResponse'

    def __init__(self, result: JoinRoomResult):
        self.id = self.msgid
        self.result_msg = result


class Chat(Packet):
    msgid = 'ChatMessage'

    # def __init__(self, player_id: int, emote: str, msg: str, timescale: float = 1, flip: bool = False):
    #     self.id = self.msgid
    #     self.player_id = player_id
    #     self.emote = emote
    #     self.msg = msg
    #     self.timescale = timescale
    #     self.flip = flip

    def __init__(self, *, room_id: int, text: str, emote: str, preanimation: str):
        self.id = self.msgid
        self.room_id = room_id
        self.text = text
        self.emote = emote
        self.preanimation = preanimation


class ChatOOC(Packet):
    msgid = 'Chat_OOC'

    def __init__(self, player_id: int, msg: str):
        self.id = self.msgid
        self.player_id = player_id
        self.msg = msg


class Join(Packet):
    msgid = 'Join'

    def __init__(self, player_id: int, player_name: str, char_id: str):
        self.id = self.msgid
        self.player_id = player_id
        self.player_name = player_name
        self.char_id = char_id


class Leave(Packet):
    msgid = 'Leave'

    def __init__(self, player_id: int):
        self.id = self.msgid
        self.player_id = player_id


class Disconnect(Packet):
    class DisconnectCause:
        UNSPECIFIED = 0
        DISCONNECT_BY_USER = 1
        KICKED = 2
        BANNED = 3

    msgid = 'Disconnect'

    def __init__(self, cause: DisconnectCause, player_id: int):
        self.id = self.msgid
        self.cause = cause
        self.player_id = player_id


class SetBackground(Packet):
    class Transition:
        class TransitionType:
            NONE = 0
            FADE_TO_BLACK = 1
            CROSSFADE = 2
            FADE_TO_WHITE = 3

        def __init__(self, transition_type: TransitionType, time: float):
            self.type = transition_type
            self.time = time

    msgid = 'SetBackground'

    def __init__(self, name: str, transition: Transition = None):
        self.id = self.msgid
        self.name = name
        self.transition = transition


class SoundPlay(Packet):
    msgid = 'SoundPlay'

    def __init__(self, name: str, channel: int, loop: bool = False):
        self.id = self.msgid
        self.name = name
        self.channel = channel
        self.loop = loop


class SoundStop(Packet):
    msgid = 'SoundStop'

    def __init__(self, channel: int):
        self.id = self.msgid
        self.channel = channel


class SoundVolume(Packet):
    msgid = 'SoundVolume'

    def __init__(self, channel: int, smooth: bool = False):
        self.id = self.msgid
        self.channel = channel
        self.smooth = smooth


class Goodbye(Packet):
    msgid = 'Goodbye'

    def __init__(self):
        self.id = self.msgid


class AssetListRequest(Packet):
    msgid = 'AssetListRequest'

    def __init__(self):
        self.id = self.msgid

class AssetListResponse(Packet):
    msgid = 'AssetListResponse'

    def __init__(self):
        self.id = self.msgid