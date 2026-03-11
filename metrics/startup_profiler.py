import time


def measure_startup(initializer):
    start = time.perf_counter()
    initializer()
    return (time.perf_counter() - start) * 1000.0
