"""Minimal request telemetry utilities."""

from time import perf_counter


class Timer:
    def __init__(self) -> None:
        self.started = perf_counter()

    @property
    def elapsed_ms(self) -> float:
        return (perf_counter() - self.started) * 1000
