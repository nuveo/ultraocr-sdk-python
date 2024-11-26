import requests

class BearerAuth(requests.auth.AuthBase):
    """ Helper for add bearer authentication in requests """

    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers['Authorization'] = f'Bearer {self.token}'
        return r

def validate_status(status: int, allowed: list[int]) -> bool:
    """Validate the status code.

    Validate the status code based on the alloweds by the route.

    Args:
        status: The request status code.
        allowed: The list of allowed status codes.
    
    Returns:
        A boolean informing whether the status is valid or not. Example: True
    """
    return status in allowed
