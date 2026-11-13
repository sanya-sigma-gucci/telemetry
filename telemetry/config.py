# Общие настройки системы
NUM_SOURCES = 4                 # 4 источника
POLL_INTERVAL_SEC = 1.0         # опрос раз в секунду
OBJECTS_MIN = 100               # минимум объектов с источника
OBJECTS_MAX = 600               # максимум объектов с источника
VALUES_PER_SOURCE_CAP = 1000    # не больше 1000 значений с источника
SCALAR_MIN, SCALAR_MAX = -1_000_000.0, 1_000_000.0

# Заранее предопределённые тренды (20 штук)
TREND_IDS = {f"trend_{i:02d}" for i in range(20)}

TREND_WINDOW = 3600             # окно видимости в памяти
DB_PATH = "telemetry.db"
INVALID_LOG = "invalid.log"