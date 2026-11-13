from dataclasses import dataclass
from typing import Any
import time


@dataclass(slots=True)
class Reading:
    source_id: int
    object_id: str
    kind: str        # "scalar" | "bool"
    value: Any       # float | bool (или мусор при невалидном значении)
    ts: float

    @classmethod
    def create(cls, source_id: int, object_id: str, kind: str, value: Any) -> "Reading":
        return cls(source_id=source_id, object_id=object_id, kind=kind, value=value, ts=time.time())