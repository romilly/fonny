import time


def wait_until(condition: callable, timeout=0.5, delay=0.1, **args) -> bool:
    """
        Repeatedly evaluates a condition function until it returns `True` or the timeout expires.

        Args:
            condition (callable): A callable function that returns a boolean value.
            timeout (float, optional): The maximum duration (in seconds) to wait for the condition to become `True`. Defaults to 0.5 seconds.
            delay (float, optional): The interval (in seconds) between successive evaluations of the condition. Defaults to 0.1 seconds.
            **args: Additional keyword arguments to pass to the condition function.

        Returns:
            bool: `True` if the condition becomes `True` within the timeout duration, otherwise `False`.
    """
    time_end = time.time() + timeout
    while time.time() < time_end:
        if condition(**args):
            return True
        time.sleep(delay)
    return False