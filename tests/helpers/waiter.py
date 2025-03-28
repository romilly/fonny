import time


def wait_until(condition: callable, timeout=0.5, delay=0.1, **args) -> bool:
    time_end = time.time() + timeout
    while time.time() < time_end:
        if condition(**args):
            return True
        time.sleep(delay)
    return False