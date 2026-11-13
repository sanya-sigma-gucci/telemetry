import logging
import signal
import time
from logging.handlers import RotatingFileHandler

from config import NUM_SOURCES, POLL_INTERVAL_SEC, TREND_IDS, INVALID_LOG
from sources import TelemetrySource
from validation import validate
from storage import Storage
from trend_journal import TrendJournal


def setup_logging() -> logging.Logger:
    logger = logging.getLogger("telemetry")
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s | %(levelname)-7s | %(message)s")

    fh = RotatingFileHandler(INVALID_LOG, maxBytes=5_000_000, backupCount=3, encoding="utf-8")
    fh.setLevel(logging.WARNING)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)
    sh.setFormatter(fmt)
    logger.addHandler(sh)
    return logger


def main() -> None:
    log = setup_logging()
    storage = Storage()
    journal = TrendJournal()
    sources = [TelemetrySource(i) for i in range(NUM_SOURCES)]

    stop = {"flag": False}

    def _handle_sig(*_a):
        stop["flag"] = True

    signal.signal(signal.SIGINT, _handle_sig)
    signal.signal(signal.SIGTERM, _handle_sig)

    log.info("Start telemetry loop (sources=%d, interval=%.1fs)", NUM_SOURCES, POLL_INTERVAL_SEC)

    total = valid = invalid = trends = 0
    t_last_report = time.time()

    try:
        while not stop["flag"]:
            tick_start = time.time()
            for src in sources:
                batch = src.poll()
                for r in batch:
                    total += 1
                    ok, reason = validate(r)
                    if ok:
                        storage.save_reading(r)
                        valid += 1
                        if r.object_id in TREND_IDS:
                            storage.save_trend(r)
                            journal.add(r)
                            trends += 1
                    else:
                        invalid += 1
                        storage.log_invalid(r, reason)
                        log.warning(
                            "invalid: src=%d obj=%s kind=%s value=%r reason=%s",
                            r.source_id, r.object_id, r.kind, r.value, reason,
                        )
            storage.commit()

            if time.time() - t_last_report >= 10:
                log.info(
                    "stats: total=%d valid=%d invalid=%d trends=%d | journal=%s",
                    total, valid, invalid, trends, journal.snapshot(),
                )
                t_last_report = time.time()

            elapsed = time.time() - tick_start
            sleep_for = POLL_INTERVAL_SEC - elapsed
            if sleep_for > 0:
                time.sleep(sleep_for)
    finally:
        storage.commit()
        storage.close()
        log.info("Stopped. total=%d valid=%d invalid=%d trends=%d",
                 total, valid, invalid, trends)


if __name__ == "__main__":
    main()