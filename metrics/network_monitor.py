from dataclasses import dataclass


@dataclass
class NetCounters:
    bytes_recv: int
    bytes_sent: int


def read_network_counters() -> NetCounters:
    recv = sent = 0
    try:
        with open('/proc/net/dev', 'r', encoding='utf-8') as f:
            for line in f.readlines()[2:]:
                parts = line.replace(':', ' ').split()
                if len(parts) >= 17:
                    recv += int(parts[1])
                    sent += int(parts[9])
    except Exception:
        pass
    return NetCounters(bytes_recv=recv, bytes_sent=sent)


def network_delta(start: NetCounters, end: NetCounters):
    return {"bytes_sent": max(0, end.bytes_sent - start.bytes_sent), "bytes_recv": max(0, end.bytes_recv - start.bytes_recv)}
