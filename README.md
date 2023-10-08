# Plus Deck 2C PC Cassette Deck

The Plus Deck 2C is a cassette deck that mounts in a 5.25" PC drive bay and is controlled over RS-232 serial. It was intended for archiving cassette tapes to mp3 - note that it can not *write* to cassettes. Here's the Amazon page for it:

<https://www.amazon.com/Plusdeck-2c-PC-Cassette-Deck/dp/B000CSGIJW>

It was initally released in the 2000s, and they are currently difficult to find. However, I always wanted one as a teenager and, as an adult, bought one for Too Much Money, and am currently writing modern tools for using it in a modern PC.

## Hardware Setup

The deck is powered by 4-pin molex and has a header, which mounts on a PCI slot on the back of your case. This header contains an RS-232 serial port and a number of 3.5mm audio jacks:

| Jack  | Basic/Advanced | Usage                                 |
|-------|----------------|---------------------------------------|
| Blue  | Basic          | Cassette line out / PC line in        |
| Pink  | Advanced       | Front microphone jack / PC microphone |
| Green | Advanced       | Front headphone jac / PC line out     |
| Black | Advanced       | Auxilliary audio out / Speakers       |

At a minimum, you need to *always* plug the Blue jack into PC line in - or, if you don't care about recording audio, directly to your receiver. The pink, green and black cables are only needed if you want to use the headphone and microphone jacks on the front of the drive - which, on a modern PC with an audio header on the motherboard, is of limited utility.

On a modern PC without a 5.25" drive or an RS-232 port, you will need:

1. An external molex power supply. This looks like a laptop power supply, but has a 4-pin molex style header. This can be casually plugged in and unplugged, at least as far as powering the deck is concerned.
2. A usb-to-RS-232 cable. You will need to use the included patch cable (or another adapter) to get the plugs/sockets to match. Note that on my machine, this exposes it on COM3 in Windows - the original Plus Deck software is, to my knowledge, hard-coded to use COM1. You can find out for sure by perusing Device Manager.

## Running the Original Software

First, you will need to set up Windows XP in Virtualbox. The directions I followed are here:

<https://eprebys.faculty.ucdavis.edu/2020/04/08/installing-windows-xp-in-virtualbox-or-other-vm/>

Second, you will need to configure Virtualbox to proxy the host's serial device to COM1 in the VM. This can be found in Settings.

Third, if you want to use the original software's MP3 encoding functionality, you will need to proxy Line In to the VM. This can also be found in Settings. However, since I merely wanted to reverse engineer the protocol, I did *not* do this and instead configured my machine to play Line In over the output sound device. That setting is buried under "More sound settings" under Sound configuration in Windows 11.

Finally, you will need to copy both the Plus Deck's software and a serial monitor to the VM. With a little configuring, you can make it so Virtualbox lets you click and drag to the desktop. The two pieces of software I used are here:

1. Plus Deck software: <https://archive.org/details/plusdeck2c>
2. Portmon serial monitor: <https://learn.microsoft.com/en-us/sysinternals/downloads/portmon>

From here, you should be able to boot the VM, install the software, launch Portmon to observe the serial port, and launch the Plus Deck software to interact with the cassette deck.

## Serial Protocol

I've made significant progress decoding the serial protocol. For more, see [protocol.md](./protocol.md).

## Software Design and Architecture

First, I intend to use rust and [serialport](https://docs.rs/serialport/latest/serialport/) to create a client library for the Plus Deck. Because of the evented nature, I will need a channels implementation - either `tokio`, `crossbeam` or stdlib. I will probably use one of the latter two.

Based on my current knowledge, I should be able to make a simple enum for commands and a simple enum for status; encode send commands from an input channel straight to the Plus Deck; decode status updates and compare to the last status; emit changes in status over a channel; and allow the last known status to be polled by the user. A little fiddly, but not bad.

This client library can include a simple CLI tool and will allow me to write comprehensive integration tests. This will be critical for confirming that my understanding of the protocol is correct, and allow me to find more edge cases and test things the original software doesn't do.

From there, I'm considering writing a gstreamer plugin for the Plus Deck. There happens to be a [rust library](https://gitlab.freedesktop.org/gstreamer/gstreamer-rs) for this, and having such a plugin should allow for getting gstreamer-enabled applications to be able to use the Plus Deck through a URI-based protocol. Note that, while we can easily treat Side A and Side B as tracks 1 and 2 respectively, we can NOT support seeking directly, as gstreamer expects those APIs to be byte-accurate.

The gstreamer plugin should enable writing a plugin for [mopidy](https://docs.mopidy.com/en/latest/), a client/server media player written in Python. This will allow me to play cassette tapes through mopidy, alongside CDs, MP3s, and other streams.

Another option is to write an application that replicates the archiving functionality of the original software. I can basically play both sides, listen on Line In, rip it through an encoder, and optionally split tracks based on quiet periods between songs. The architecture for this is TBD. We may also be able to add/incorporate support for [kansas city standard](http://www.dabeaz.com/py-kcs/) tapes, if I want to support my retro hobby.
