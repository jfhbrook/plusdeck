# Hardware Setup

The deck is powered by 4-pin molex and has a header, which mounts on a PCI slot
on the back of your case. This header contains an RS-232 serial port and a
number of 3.5mm audio jacks:

| Jack  | Basic/Advanced | Usage                                 |
|-------|----------------|---------------------------------------|
| Blue  | Basic          | Cassette line out / PC line in        |
| Pink  | Advanced       | Front microphone jack / PC microphone |
| Green | Advanced       | Front headphone jac / PC line out     |
| Black | Advanced       | Auxilliary audio out / Speakers       |

At a minimum, you need to *always* plug the Blue jack into PC line in - or, if
you don't care about recording audio, directly to your receiver. The pink,
green and black cables are only needed if you want to use the headphone and
microphone jacks on the front of the drive - which, on a modern PC with an
audio header on the motherboard, is of limited utility.

On a modern PC without a 5.25" drive or an RS-232 port, you will need:

1. An external molex power supply. This looks like a laptop power supply, but
   has a 4-pin molex style header. This can be casually plugged in and
   unplugged, at least as far as powering the deck is concerned.
2. A usb-to-RS-232 cable. You will need to use the included patch cable (or
   another adapter) to get the plugs/sockets to match. Note that on my machine,
   this exposes it on COM3 in Windows - the original Plus Deck software is, to
   my knowledge, hard-coded to use COM1. You can find out for sure by perusing
   Device Manager.
