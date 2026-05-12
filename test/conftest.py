import logging
import os


def pytest_configure(config):
    level_name = os.environ.get("DFTT_TEST_LOG_LEVEL", "DEBUG").upper()
    level = getattr(logging, level_name, logging.DEBUG)
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d-%(funcName)s()] %(message)s",
    )
    logging.getLogger("dftt_timecode").setLevel(level)
