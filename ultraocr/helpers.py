import requests
from enum import Enum

class BearerAuth(requests.auth.AuthBase):
    """ Helper for add bearer authentication in requests """

    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers['Authorization'] = f'Bearer {self.token}'
        return r
    
class Resource(Enum):
    JOB = 'job'
    BATCH = 'batch'

class TimeoutException(Exception):
    """ Timeout exception """
    pass