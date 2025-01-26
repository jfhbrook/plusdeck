# Plus Deck 2C Serial Protocol

## Commands

Commands are sent as individual bytes:

| byte (dec) | byte (hex) | byte (binary) | command      |
|------------|------------|---------------|--------------|
| 01         | 01         | 0000 0001     | play side A  |
| 02         | 02         | 0000 0010     | play side B  |
| 03         | 03         | 0000 0011     | fast-forward |
| 04         | 04         | 0000 0100     | rewind       |
| 05         | 05         | 0000 0101     | toggle pause |
| 06         | 06         | 0000 0110     | stop         |
| 08         | 08         | 0000 1000     | eject        |
| 11         | 0B         | 0000 1011     | subscribe    |
| 12         | 0C         | 0000 1100     | unsubscribe  |

These *appear* to be more or less in-order, though that leaves questions about the significance of skipping 0x07 (7) and 0x09-0x0A (9-10). On a cursory glance, there don't seem to be any significant byte masks, range starts, etc. The most likely scenario is that 0x00 and 0xA are reserved, and subscribe/unsubscribe exist on a block that starts at 0x0A.

It's believed that this is more or less exhaustive. Clicking other buttons, such as looping behavior, don't seem to send commands - it's believed this behavior is implemented in software - and the device doesn't advertise any other behavior, such as writing to tape (the mic jack seems entirely for proxying to the front panel). That said, testing some other bytes to see what happens may be worthwhile.

## Statuses

Statuses are emitted in a relatively tight loop as individual bytes:

| byte (dec) | byte (hex) | byte (binary) | status                           |
|------------|------------|---------------|----------------------------------|
| 10         | 0A         | 0000 1010     | playing side A                   |
| 12         | 0C         | 0000 1100     | paused on side A (unsubscribe 1) |
| 20         | 14         | 0001 0100     | playing side B                   |
| 21         | 15         | 0001 0101     | ready/subscribed                 |
| 22         | 16         | 0001 0110     | paused on side B (unsubscribe 2) |
| 30         | 1E         | 0001 1110     | fast-forwarding                  |
| 40         | 28         | 0010 1000     | rewinding                        |
| 50         | 32         | 0011 0010     | stopped                          |
| 60         | 3C         | 0011 1100     | ejected                          |

Note that I have not produced any error codes - hitting buttons twice is idempotent, and hitting buttons on eject does not yield any code other than 0x3C (60).

Unlike commands, there are a few clear relationships between the bytes chosen. Categories are chosen starting at multiples of 10:

| Range Start | Meaning               |
| ------------|-----------------------|
| 10 (0x0A)   | Play/Pause, Side A    |
| 20 (0x14)   | Play/Pause, Side B    |
| 30 (0x1E)   | Fast Movement, Side A |
| 40 (0x28)   | Fast Movement, Side B |
| 50 (0x32)   | Stopped               |
| 60 (0x3C)   | Ejected               |

In addition, play and pause commands are separated by 2. For example, playing side A is 10 (0x0A), while pausing side A is 12 (0x0C) = 10 + 2.

The outlier is ready/subscribed, at 21 (0x15), right in between playing B (20) and paused B (22). I believe this event is an accident. My evidence for this is that there isn't a clear event for unsubscribing. Instead, the device either emits 12 (0x0C) or 22 (0x16), - paused on A and paused on B respectively. This makes me think that some incidental aspect of the device's design causes it to emit these bytes, and that, while that behavior seems reliable, it's not intentional.

Something I haven't tried is seeing if plugging/unplugging headphones triggers
any events. I don't expect them but it's worth checking.
