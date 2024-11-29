from enum import Enum


POOLING_INTERVAL = 1
API_TIMEOUT = 30
UPLOAD_TIMEOUT = 120
DEFAULT_EXPIRATION_TIME = 60
BASE_URL = "https://ultraocr.apis.nuveo.ai/v2"
AUTH_BASE_URL = "https://auth.apis.nuveo.ai/v2"
STATUS_DONE = "done"
STATUS_ERROR = "error"


class Resource(Enum):
    """Resource type"""

    JOB = "job"
    BATCH = "batch"
