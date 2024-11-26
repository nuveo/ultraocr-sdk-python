import requests
import time
from ultraocr.helpers import BearerAuth
from ultraocr.enums import Resource
from ultraocr.exceptions import TimeoutException

class Client:
    """ UltraOCR Client """
    API_TIMEOUT = 30
    BASE_URL = "https://ultraocr.apis.nuveo.ai/v2/"
    AUTH_BASE_URL = "https://auth.apis.nuveo.ai/v2/"

    def __init__(
        self,
        auth_base_url: str = AUTH_BASE_URL,
        base_url: str = BASE_URL,
        timeout: int = API_TIMEOUT,
    ):
        self.auth_base_url = auth_base_url
        self.base_url = base_url
        self.timeout = timeout
        self.token = ""

    def _bearer_token(self):
        return BearerAuth(self.token)

    def authenticate(self, client_id: str, client_secret: str) -> None:
        """Authenticate on UltraOCR.

        Authenticate on UltraOCR and save the token to use on future requests.

        Args:
            client_id: The Client ID generated on Web Interface.
            client_secret: The Client Secret generated on Web Interface.
        """
        url = f"{self.auth_base_url}/token"
        data = {
            "ClientID": client_id,
            "ClientSecret": client_secret,
        }

        resp = requests.post(url, json=data)
        self.token = resp.json()["token"]

    def send_job_single_step(
        self,
        service: str,
        file: str,
        metadata: dict = None,
        params: dict = None,
    ):
        """Send job in a single step on UltraOCR.

        Send job in a single step on UltraOCR, it's faster than usual method,
        but have a 6MB as body limit (including metadata and base64 file)

        Args:
            service: The the type of document to be send.
            file: The file in base64 format.
            metadata: The metadata based on UltraOCR Docs format, optional in most cases.
            params: The query parameters given on UltraOCR Docs, optional in most cases.
        
        Returns:
            A json response containing the id and the status_url. For example:

            {
                "id": "0ujsszwN8NRY24YaXiTIE2VWDTS",
                "status_url": "https://ultraocr.apis.nuveo.ai/v2/ocr/job/result/0ujsszwN8NRY24YaXiTIE2VWDTS"
            }
        """
        # TODO facematch/extra document
        body = {
            **metadata,
            "data": file,
        }
        url = f"{self.base_url}/job/send/{service}"
        resp = requests.post(url, auth=self._bearer_token(), json=body, params=params)
        return resp.json()

    def generate_signed_url(
        self,
        service: str,
        metadata: dict = None,
        params: dict = None,
        resource: Resource = Resource.JOB,
    ):
        url = f"{self.base_url}/{resource}/{service}"
        resp = requests.post(url, auth=self._bearer_token(), json=metadata, params=params)
        return resp.json()

    def get_batch_status(self, batch_id: str):
        route = f"{self.base_url}/batch/status/{batch_id}"
        resp = requests.get(route, auth=self._bearer_token())
        return resp.json()

    def get_job_result(self, batch_id: str, job_id: str):
        route = f"{self.base_url}/job/result/{batch_id}/{job_id}"
        resp = requests.get(route, auth=self._bearer_token())
        return resp.json(), resp.status_code

    def send_job(
        self,
        service: str,
        file_path: str,
        metadata: dict = None,
        params: dict = None,
    ):
        # TODO facematch/extra document
        with open(file_path, "rb") as file_bin:
            data = file_bin.read()

        res = self.generate_signed_url(service, metadata, params, Resource.JOB)
        url = res.get("urls", {}).get("document")
        requests.put(url, data=data)

    def send_batch(self, service: str, file_path: str, metadata: dict = None, params: dict = None):
        with open(file_path, "rb") as file_bin:
            data = file_bin.read()

        res = self.generate_signed_url(service, metadata, params, Resource.BATCH)
        url = res.get("urls", {}).get("document")
        requests.put(url, data=data)

    def send_job_base64(
        self,
        service: str,
        file: str,
        metadata: dict = None,
        params: dict = None,
    ):
        # TODO facematch/extra document
        params = {
            **params,
            "base64": "true",
        }

        res = self.generate_signed_url(service, metadata, params, Resource.JOB)
        url = res.get("urls", {}).get("document")
        requests.put(url, data=file)

    def send_batch_base64(
        self,
        service: str,
        file: str,
        metadata: dict = None,
        params: dict = None,
    ):
        params = {
            **params,
            "base64": "true",
        }
        res = self.generate_signed_url(service, metadata, params, Resource.BATCH)

        url = res.get("urls", {}).get("document")
        requests.put(url, data=file)

    def wait_for_job_done(self, batch_id: str, job_id: str):
        timeout_start = time.time()
        code = None
        res = None

        while time.time() < timeout_start + self.timeout:
            res, code = self.get_job_result(batch_id, job_id)

            status = res["status"]
            if status == "done" or status == "error":
                break

            time.sleep(1)

        if time.time() > timeout_start + self.timeout:
            raise TimeoutException(self.timeout, res)

        return res, code

    def wait_for_batch_done(self, batch_id: str):
        timeout_start = time.time()
        code = None
        res = None

        while time.time() < timeout_start + self.timeout:
            res, code = self.get_batch_status(batch_id)

            status = res["status"]
            if status == "done" or status == "error":
                break

            time.sleep(1)

        if time.time() > timeout_start + self.timeout:
            raise TimeoutException(self.timeout, res)

        for job in res["jobs"]:
            job_id = job["job_ksuid"]
            self.wait_for_job_done(batch_id, job_id)

        return res, code
