import time
from contextlib import contextmanager


@contextmanager
def timed():
    start = time.perf_counter()
    out = {"start": start}
    try:
        yield out
    finally:
        out["end"] = time.perf_counter()
        out["duration"] = out["end"] - start
