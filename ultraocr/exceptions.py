class TimeoutException(Exception):
    """ Timeout exception """
    def __init__(self, timeout, last_res):
        super(f"timeout reached | timeout: {timeout} | last response: {last_res}")

class InvalidStatusCodeException(Exception):
    """ Invalid status code exception """
