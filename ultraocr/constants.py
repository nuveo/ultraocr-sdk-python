from enum import Enum


POOLING_INTERVAL = 1
API_TIMEOUT = 30
UPLOAD_TIMEOUT = 120
BASE_URL = "https://ultraocr.apis.nuveo.ai/v2/"
AUTH_BASE_URL = "https://auth.apis.nuveo.ai/v2/"


class Resource(Enum):
    """Resource type"""

    JOB = "job"
    BATCH = "batch"
