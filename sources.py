import random
from config import (
    NUM_SOURCES, OBJECTS_MIN, OBJECTS_MAX,
    VALUES_PER_SOURCE_CAP, TREND_IDS,
)
from models import Reading


class TelemetrySource:
    """
    Эмулятор источника телеметрии.
    Раз в секунду отдаёт батч из 100..600 объектов (значения scalar|bool),
    с ограничением не более 1000 значений на батч.
    """

    def __init__(self, source_id: int, rng: random.Random | None = None):
        self.source_id = source_id
        self.rng = rng or random.Random(source_id * 1000 + 7)

    def poll(self) -> list[Reading]:
        n_objects = self.rng.randint(OBJECTS_MIN, OBJECTS_MAX)
        n_objects = min(n_objects, VALUES_PER_SOURCE_CAP)

        readings: list[Reading] = []
        trend_list = list(TREND_IDS)

        for _ in range(n_objects):
            # ~2% объектов — "трендовые"
            if self.rng.random() < 0.02:
                obj_id = self.rng.choice(trend_list)
            else:
                obj_id = f"src{self.source_id}_obj{self.rng.randint(0, 500)}"

            kind = "scalar" if self.rng.random() < 0.7 else "bool"

            if kind == "scalar":
                value = self.rng.uniform(-10_000.0, 10_000.0)
                # 1.5% — портим значение (невалидное)
                if self.rng.random() < 0.015:
                    value = self.rng.choice(
                        [float("nan"), float("inf"), -float("inf"), None, "not-a-number", True]
                    )
            else:
                value = self.rng.choice([True, False])
                if self.rng.random() < 0.015:
                    value = self.rng.choice([None, "yes", 1, 0, "true"])

            readings.append(Reading.create(self.source_id, obj_id, kind, value))

        # Жёсткий кап на 1000 значений с источника
        if len(readings) > VALUES_PER_SOURCE_CAP:
            readings = readings[:VALUES_PER_SOURCE_CAP]
        return readings