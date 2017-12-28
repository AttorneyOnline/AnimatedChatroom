Obviously, this is the most important part of the entire game.

Chat:
{
    player_id: uint32
    emote: string

    // Messages can contain markup. Will be explained separately.
    msg: text

    // The timescale should be clamped to reasonable values,
	// e.g. 0.5~4.0. This modifies the speed at which the
	// chat message is performed, along with the associated
	// emote.
    (timescale: float)

	// Depending on the game, horizontal flipping may not be available
	// as an option to clients; however, it may be controlled
	// by the server programmatically.
    (flip: bool)

    [..other options follow based on the game..]
}
Attorney Online 3 extensions:
{
    (preanim: bool)

    // The asset should have marked a default side.
    // But it can be overridden...
    (side: enum {
        WITNESS = 0
        DEFENSE = 1
        PROSECUTION = 2
        JUDGE = 3
        // don't remember what these stood for...
        HLD = 4
        HLP = 5
    })

    (objection: enum {
        NONE = 0
        HOLD_IT = 1
        OBJECTION = 2
        TAKE_THAT = 3
        CUSTOM = 4
    })

    (realization: bool)
    (evidence_id: uint32)
}

Chat_OOC:
{
    player_id: uint32
    msg: text
}

Join:
{
    player_id: uint32
    player_name: string
    char_id: string
}

Leave:
{
    player_id: uint32
}

Disconnect:
{
    cause: enum {
        UNSPECIFIED = 0
        DISCONNECT_BY_USER = 1
        KICKED = 2
        BANNED = 3
    }
    player_id: uint32
}

SetBackground:
{
    name: string
    (transition: {
        type: enum {
            NONE = 0
            FADE_TO_BLACK = 1
            CROSSFADE = 2
            FADE_TO_WHITE = 3
        }
        time: float
    })
}

SoundPlay:
{
    name: string
    (loop: bool)
    channel: uint32
}

SoundStop:
{
    channel: uint32
    (fade_time: float) // in seconds
}

SoundVolume:
{
    channel: uint32
    (smooth: bool)
}