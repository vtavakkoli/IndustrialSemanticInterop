import os
import threading
import time
import tracemalloc


class ResourceMonitor:
    def __init__(self, interval_sec: float = 0.05):
        self.interval_sec = interval_sec
        self._running = False
        self.cpu = []
        self.mem = []
        self._thread = None

    def _run(self):
        while self._running:
            try:
                self.cpu.append(float(os.getloadavg()[0]))
            except Exception:
                self.cpu.append(0.0)
            current, _ = tracemalloc.get_traced_memory()
            self.mem.append(current / (1024 * 1024))
            time.sleep(self.interval_sec)

    def start(self):
        tracemalloc.start()
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=1)
        tracemalloc.stop()

    @property
    def cpu_avg(self):
        return float(sum(self.cpu) / len(self.cpu)) if self.cpu else 0.0

    @property
    def mem_avg(self):
        return float(sum(self.mem) / len(self.mem)) if self.mem else 0.0
