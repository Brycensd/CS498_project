from dataclasses import dataclass

from core.events import EventBus


@dataclass(frozen=True)
class Ping:
    n: int


@dataclass(frozen=True)
class Pong:
    n: int


def test_publish_reaches_only_subscribers_of_that_type():
    bus = EventBus()
    pings, pongs = [], []
    bus.subscribe(Ping, pings.append)
    bus.subscribe(Pong, pongs.append)

    bus.publish(Ping(1))

    assert pings == [Ping(1)]
    assert pongs == []


def test_unsubscribe():
    bus = EventBus()
    seen = []
    unsubscribe = bus.subscribe(Ping, seen.append)
    unsubscribe()
    unsubscribe()  # second call is harmless

    bus.publish(Ping(1))

    assert seen == []


def test_failing_handler_does_not_block_others():
    bus = EventBus()
    seen = []

    def broken(_event):
        raise RuntimeError("boom")

    bus.subscribe(Ping, broken)
    bus.subscribe(Ping, seen.append)

    bus.publish(Ping(2))

    assert seen == [Ping(2)]
