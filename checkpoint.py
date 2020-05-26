import time
from typing import Iterator


def time_from_last_checkpoint() -> Iterator[float]:
    """
    Generator returning seconds elapsed since the previous call of the generator
    """
    start = time.time()
    yield 0.0
    while True:
        last_checkpoint = time.time()
        yield last_checkpoint - start
        start = last_checkpoint
