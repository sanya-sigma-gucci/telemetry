import math
from config import SCALAR_MIN, SCALAR_MAX, TREND_IDS
from models import Reading


def validate(r: Reading) -> tuple[bool, str]:
    """Возвращает (валидно?, причина_отказа)."""
    # Идентификатор объекта
    if not r.object_id or not isinstance(r.object_id, str):
        return False, "invalid object_id"

    # Тип значения
    if r.kind == "bool":
        if not isinstance(r.value, bool):
            return False, f"expected bool, got {type(r.value).__name__}={r.value!r}"
        return True, ""

    if r.kind == "scalar":
        v = r.value
        # bool — подкласс int, отделяем явно
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            return False, f"expected number, got {type(v).__name__}={v!r}"
        if not math.isfinite(v):
            return False, f"non-finite value: {v!r}"
        if not (SCALAR_MIN <= v <= SCALAR_MAX):
            return False, f"out of range [{SCALAR_MIN}, {SCALAR_MAX}]: {v!r}"
        # для трендов дополнительная защита — не допускаем None/строк
        if r.object_id in TREND_IDS and not isinstance(v, (int, float)):
            return False, "trend scalar has wrong type"
        return True, ""

    return False, f"unknown kind: {r.kind!r}"