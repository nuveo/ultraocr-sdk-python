import requests
from ultraocr.constants import UPLOAD_TIMEOUT
from ultraocr.exceptions import InvalidStatusCodeException


class BearerAuth(requests.auth.AuthBase):
    """Helper for add bearer authentication in requests"""

    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["Authorization"] = f"Bearer {self.token}"
        return r


def upload_file(url: str, file_path: str):
    """Upload file.

    Open and upload file

    Args:
        url: The url to upload the file.
        file_path: The file path.

    Returns:
        The request output.
    """
    with open(file_path, "rb") as file_bin:
        data = file_bin.read()

    return requests.put(url, data=data, timeout=UPLOAD_TIMEOUT)


def validate_status_code(status: int, want: int):
    """Validate status code.

    Validate status code and raise excepction if invalid.

    Args:
        status: The response status code.
        want: The expected status code.

    Raises:
        InvalidStatusCodeException: If status isn't valid.
    """
    if status != want:
        raise InvalidStatusCodeException(status, want)
