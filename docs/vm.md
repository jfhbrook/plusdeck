# Running the Original Software in a Windows XP VM

The original software reportedly works in Windows 11. However, I did my
testing in a period-appropriate Windows XP VM. This is how I did it.

First, you will need to set up Windows XP in Virtualbox. The directions I
followed are here:

<https://eprebys.faculty.ucdavis.edu/2020/04/08/installing-windows-xp-in-virtualbox-or-other-vm/>

Second, you will need to configure Virtualbox to proxy the host's serial device
to COM1 in the VM. This can be found in Settings.

Third, if you want to use the original software's MP3 encoding functionality,
you will need to proxy Line In to the VM. This can also be found in Settings.
However, since I merely wanted to reverse engineer the protocol, I did *not* do
this and instead configured my machine to play Line In over the output sound
device. That setting is buried under "More sound settings" under Sound
configuration in Windows 11.

Finally, you will need to copy both the Plus Deck's software and a serial
monitor to the VM. With a little configuring, you can make it so Virtualbox
lets you click and drag to the desktop. The two pieces of software I used are
here:

1. Plus Deck software: <https://archive.org/details/plusdeck2c>
2. Portmon serial monitor: <https://learn.microsoft.com/en-us/sysinternals/downloads/portmon>

From here, you should be able to boot the VM, install the software, launch
Portmon to observe the serial port, and launch the Plus Deck software to
interact with the cassette deck.
