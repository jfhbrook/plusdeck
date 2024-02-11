# Plus Deck 2C Serial Protocol

## Commands

Commands are sent as individual bytes:

| byte (hex) | byte (binary) | command      |
|------------|---------------|--------------|
| 01         | 0000 0001     | play side A  |
| 02         | 0000 0010     | play side B  |
| 03         | 0000 0011     | fast-forward |
| 04         | 0000 0100     | rewind       |
| 05         | 0000 0101     | toggle pause |
| 06         | 0000 0110     | stop         |
| 08         | 0000 1000     | eject        |
| 0B         | 0000 1011     | up/listen    |
| 0C         | 0000 1100     | (shut)down   |

These *appear* to be more or less in-order, though that leaves questions about
the significance of skipping 0x07 and 0x09-0x0A. On a cursory glance, there
don't seem to be any significant byte masks.

It's believed that this is more or less exhaustive. Clicking other buttons,
such as looping behavior, don't seem to send commands - it's believed this
behavior is implemented in software - and the device doesn't advertise any
other behavior, such as writing to tape (the mic jack seems entirely for
proxying to the front panel). That said, testing some other bytes to see what
happens may be worthwhile.

## Statuses

Statuses are emitted in a relatively tight loop as individual bytes:

| byte (hex) | byte (binary) | status           |
|------------|---------------|------------------|
| 0A         | 0000 1010     | playing side A   |
| 0C         | 0000 1100     | paused on side A |
| 14         | 0001 0100     | playing side B   |
| 15         | 0001 0101     | ready            |
| 16         | 0001 0110     | paused on side B |
| 1E         | 0001 1110     | fast-forwarding  |
| 28         | 0010 1000     | rewinding        |
| 32         | 0011 0010     | stopped          |
| 3C         | 0011 1100     | ejected          |

Note that I have not produced any error codes - hitting buttons twice is
idempotent, and hitting buttons on eject does not yield any code other than
0x3C.

Unlike commands, there doesn't seem to be an obvious rhyme or reason to the
ordering of the statuses. I'm wondering if bits have individual meaning, but
it's not penciling out:

1. `PLAY_A & PAUSE_A == 0x08` and `PLAY_B & PAUSE_B == 0x14` - I don't think
   this implies anything. Though, pause is always 2 more than the corresponding
   play state.
2. `PLAY_A & PLAY_B  == 0x00` and `PAUSE_A & PAUSE_B == 0x04` - that suggests
   no byte for the side, and also that the hunch on bits for sides isn't
   panning out.
3. `FAST_FORWARD & REWIND == 0x08`, so byte 4 may indicate fast movement;
   however they don't combine with `PLAY_A` or `PLAY_B` in any clean manner

Current data suggests that there isn't a bit masking scheme. However, it may
be worth revisiting if tests reveal mistakes in reverse engineering the codes.

Something I haven't tried is seeing if plugging/unplugging headphones triggers
any events. I don't expect them but it's worth checking.

Note that on command 0x0B (up), we receive a single 0x15 before seeing either
0x32 or 0x3C. This appears consistent and doesn't obviously collide with
another status, and is currently presumed to mean "ready".

However, on command 0x0c (down), we seem to receive either 0x0C or 0x16 (pause
states) before it stops. I believe this latter case is just a quirk in how the
shutdown procedures work on the hardware level and is mostly noise. This
suggests, however, that 0x15 *might* also be noise on some level, though that
would make the most sense if there's a bit-masking scheme we're missing.
