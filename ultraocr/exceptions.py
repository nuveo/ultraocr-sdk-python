""" Module providing the UltraOCR SDK exceptions """


class TimeoutException(Exception):
    """Timeout exception"""

    def __init__(self, timeout: int, last_res):
        super().__init__(
            f"timeout reached | timeout: {timeout} | last response: {last_res}"
        )


class InvalidStatusCodeException(Exception):
    """Invalid status code exception"""

    def __init__(self, status: int, expected: int):
        super().__init__(f"Invalid status code | got: {status} | expect: {expected}")
