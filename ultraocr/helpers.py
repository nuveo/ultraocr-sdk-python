import requests


class BearerAuth(requests.auth.AuthBase):
    """Helper for add bearer authentication in requests"""

    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["Authorization"] = f"Bearer {self.token}"
        return r
