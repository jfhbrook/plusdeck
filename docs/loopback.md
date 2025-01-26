# Loopback

The standard configuration of the Plus Deck 2C has its audio output connected to Line In on the host PC's sound card. The PC is then expected to play the input from Line In on its Line Out. This configuration is known as a "loopback".

In my experience, Windows and MacOS allow for configuring this loopback in the standard sound UI. Until I hear that I'm remembering wrong, I won't be documenting its setup in those operating systems. However, Linux is more complex.

## Pulseaudio

If you are using Pulseaudio, you can configure a loopback on the fly with the `pactl` command:

```sh
# Enable loopback
pactl load-module module-loopback latency_msec=1

# Disable loopback
pactl unload-module module-loopback
```

Doing this on an ad-hoc basis may be desirable, as there may be low level noise on Line In, depending on your configuration.

To do this permanently with Pulseaudio, you should be able to add the following line to `/etc/pulse/default.pa`:

```sh
load-module module-loopback latency_msec=1
```

## Pipewire

Many modern Linux distributions, such as Fedora Linux, use a new audio server called Pipewire. Pipewire is significantly more powerful than Pulseaudio, but also more complex.

While loopback may be configured natively in Pipewire, I've found the most straightforward way is to use its Pulseaudio compatibility layer. You may need to install this layer manually, if it's not included in your distribution. For example, in Fedora:

```sh
sudo dnf install pipewire-pulseaudio
```

Once this is installed, the `pactl` commands mentioned previously should work as expected.

To set this up permanently using `pipewire-pulseaudio`, edit `/etc/pipewire/pipewire-pulse.conf`, find an array called `pulse.cmd`, and add an entry like the following:

```
pulse.cmd = [
    # ...
    { cmd = "load-module" args = "module-loopback" flags = [ latency_msec=1 ] }
]
```
