from dataclasses import dataclass


@dataclass(frozen=True)
class WorkloadProfile:
    name: str
    message_count: int
    payload_size: int
    concurrency: int


WORKLOAD_PROFILES = {
    "small": WorkloadProfile("small", message_count=120, payload_size=128, concurrency=1),
    "medium": WorkloadProfile("medium", message_count=360, payload_size=512, concurrency=2),
    "large": WorkloadProfile("large", message_count=900, payload_size=2048, concurrency=4),
}
