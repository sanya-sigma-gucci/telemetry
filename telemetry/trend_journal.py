from collections import deque, defaultdict
from config import TREND_WINDOW
from models import Reading


class TrendJournal:
    """
    Журнал трендов с постоянным окном видимости.
    Общее окно — TREND_WINDOW (3600), плюс отдельное окно на каждый тренд.
    """

    def __init__(self, window: int = TREND_WINDOW):
        self.window_size = window
        self._global: deque[Reading] = deque(maxlen=window)
        self._per_trend: dict[str, deque[Reading]] = defaultdict(lambda: deque(maxlen=window))

    def add(self, r: Reading) -> None:
        self._global.append(r)
        self._per_trend[r.object_id].append(r)

    def latest(self, n: int = 10) -> list[Reading]:
        return list(self._global)[-n:]

    def snapshot(self) -> dict[str, int]:
        return {
            "global_size": len(self._global),
            "per_trend_sizes": {k: len(v) for k, v in self._per_trend.items()},
        }