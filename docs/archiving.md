## Archiving

### Music Tapes

The Plus Deck was originally intended for ripping music tapes to MP3, and this
is the core functionality of the original software.

Replicating this functionality would mean doing something like:

1. Playing the cassette all the way through, on both sides
2. Detecting pauses in the audio and treating them as track breaks
3. Naming and tagging the ripped tracks accordingly.

I have not investigated that possibility past this point.

### Digital Tapes

There isn't any particular reason why it can't be used to archive digital
tapes, as used by many 8-bit computers. In fact, this could be a major use
case.

The major piece of prior art for this is David Beazley's work to decode
Superboard II cassettes, which are written in a format called Kansas City
Standard:

<http://www.dabeaz.com/py-kcs/>

My understanding is that the vast majority of digital cassettes from the 8-bit
era used some variation of KCS.

I have not investigated this possibility further than reading David's blog
posts.
