import logging
import time

logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
formatter = logging.Formatter("[{asctime} {levelname}] [ redcap ] {message}", style="{")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
logger.setLevel(logging.DEBUG)


def simulate_network_request(
    wait_seconds: int, addl_log_prefix: str = ""
) -> list[dict]:
    """Simulates making a network request by waiting for a specified amount of seconds."""
    logger.debug(
        f"{addl_log_prefix + ' ' if addl_log_prefix else ''}Simulating request of {wait_seconds} second(s).... "
    )
    time.sleep(wait_seconds)
    logger.debug(f"{addl_log_prefix + ' ' if addl_log_prefix else ''}Done")
    return [dict()]
