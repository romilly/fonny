import time


def wait_until(condition: callable, args=None, timeout=0.5, delay=0.1) -> bool:
    args = args or []
    time_end = time.time() + timeout
    while time.time() < time_end:
        if condition(*args):
            return True
        time.sleep(delay)
    return False