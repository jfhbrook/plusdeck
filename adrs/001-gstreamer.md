# ADR 001 - Gstreamer Plugin

### Status: Accepted

### Josh Holbrook

## Context

My current strategy for interacting with the Plus Deck is a Python library. However, I've considered writing a gstreamer plugin.

The motivation for a gstreamer plugin is allowing for the Plus Deck to be used as a general purpose player in gstreamer-based applications, such as [mopidy](https://docs.mopidy.com/en/latest/). In theory, a gstreamer plugin plus a mopidy plugin would allow me to play cassette tapes through mopidy, alongside CDs, MP3s, and other streams.

Gstreamer applications are typically written in C++. However, there happens to be a [rust library](https://gitlab.freedesktop.org/gstreamer/gstreamer-rs). Using rust would likely make the serial parts easier.

Unfortunately, there are a number of challenges when it comes to a gstreamer plugin. Typically, plugins expect URLs to correspond to discrete tracks, and they expect seeking to have byte-level precision. While we can treat Side A and Side B as tracks, it is not possible to seek even to particular positions, much less anything resembling a byte - after all, cassettes are an analog medium.

## Decision

A Gstreamer plugin, or similar, will not be implemented for the Plus Deck 2C. The semantics of tape are too different from those of digital media to do so with an acceptable impedance mismatch.
