import asyncio
from dataclasses import replace

import ipywidgets as widgets
from serial.tools.list_ports import comports

from plusdeck.client import Client, Command, State
from plusdeck.config import Config

"""
ipywidgets widgets and other tools for interacting with the Plus Deck 2C PC
Cassette Deck through Jupyter.
"""


class ConfigEditor(widgets.VBox):
    """A widget for editing a Plus Deck 2C PC Cassette Deck config."""

    _config: Config
    _port_widget: widgets.SelectMultiple

    def __init__(self, config: Config):
        ports = [port.device for port in comports(include_links=True)]
        self._config = config
        self._port_widget = widgets.SelectMultiple(
            options=ports,
            value=(config.port,) if config.port in ports else ports[0:1],
            description="Serial Port",
            disabled=False,
        )
        super(ConfigEditor, self).__init__([self._port_widget])

    @property
    def value(self) -> Config:
        """The value of the current config."""

        self._config = replace(self._config, port=self._port_widget.value[0])
        return self._config


STATES = {
    State.PlayingA: "Play Side A",
    State.PausedA: "Pause Side A",
    State.PlayingB: "Play Side B",
    State.PausedB: "Pause Side B",
    State.FastForwarding: "Fast-Forward",
    State.Rewinding: "Rewind",
    State.Stopped: "Stop",
    State.Ejected: "Eject",
    State.Subscribing: "Hello",
    State.Subscribed: "Hello",
    State.Unsubscribing: "Goodbye",
    State.Unsubscribed: "Off",
}


async def player(client: Client) -> widgets.HBox:
    """Create a player widget for the Plus Deck 2C PC Cassette Deck."""

    rcv = await client.subscribe()

    status = widgets.Label(
        value="Off",
        layout={"height": "60%"},
        style={"font_family": "monospace", "font_size": "24pt"},
    )

    async def display_state():
        async for state in rcv:
            status.value = STATES[state]

    asyncio.get_running_loop().create_task(display_state())

    pause = widgets.Button(
        value=False, description="⏸️", tooltip="Pause", layout={"width": "95%"}
    )

    @pause.on_click
    def on_pause(button):
        client.send(Command.Pause)

    play_a = widgets.Button(
        value=False, description="▶️", tooltip="Play Side A", layout={"width": "45%"}
    )

    @play_a.on_click
    def on_play_a(button):
        client.send(Command.PlayA)

    play_b = widgets.Button(
        value=False, description="◀️", tooltip="Play Side B", layout={"width": "45%"}
    )

    def on_play_b(button):
        client.send(Command.PlayB)

    play_b.on_click(on_play_b)

    stop = widgets.Button(
        value=False, description="⏹️", tooltip="Stop", layout={"width": "95%"}
    )

    @stop.on_click
    def on_stop(button):
        client.send(Command.Stop)

    eject = widgets.Button(value=False, description="⏏️", tooltip="Eject")

    @eject.on_click
    def on_eject(button):
        client.send(Command.Eject)

    fast_forward = widgets.Button(value=False, description="⏩", tooltip="Fast-Forward")

    @fast_forward.on_click
    def on_fast_forward(button):
        client.send(Command.FastForward)

    rewind = widgets.Button(value=False, description="⏪", tooltip="Rewind")

    @rewind.on_click
    def on_rewind(button):
        client.send(Command.Rewind)

    power = widgets.Button(value=False, description="⏻", tooltip="Turn On/Off")

    @power.on_click
    def on_power(button):
        client.send(Command.Unsubscribe)

    return widgets.HBox(
        [
            widgets.VBox([pause, widgets.HBox([play_b, play_a]), stop]),
            widgets.VBox([status, widgets.HBox([eject, rewind, fast_forward, power])]),
        ]
    )
