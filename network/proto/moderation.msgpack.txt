Not very important.

KickPlayer:
{
    player_id: uint32
    reason: string
}

BanPlayer:
{
    player_id: uint32
    duration: uint64 // in seconds
    reason: string
}

UnbanPlayer:
{
    player: string
}

MutePlayer:
{
    player_id: uint32
    muted: bool
}

SetServerInfo:
{
    desc: string
}

-----

CreateRoom:
{
    room_id: uint32
}

DeleteRoom:
{
    room_id: uint32
}

FreezeRoom:
{
    room_id: uint32
    frozen: bool
}