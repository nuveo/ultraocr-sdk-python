import requests
import time
from ultraocr.helpers import BearerAuth
from ultraocr.enums import Resource
from ultraocr.exceptions import TimeoutException


class Client:
    """UltraOCR Client

    Client to help on UltraOCR usage. For more details about all arguments and returns,
    access the oficial system documentation on https://docs.nuveo.ai/ocr/v2/.

    """

    POOLING_INTERVAL = 1
    API_TIMEOUT = 30
    BASE_URL = "https://ultraocr.apis.nuveo.ai/v2/"
    AUTH_BASE_URL = "https://auth.apis.nuveo.ai/v2/"

    def __init__(
        self,
        auth_base_url: str = AUTH_BASE_URL,
        base_url: str = BASE_URL,
        timeout: int = API_TIMEOUT,
        interval: int = POOLING_INTERVAL,
    ):
        self.auth_base_url = auth_base_url
        self.base_url = base_url
        self.timeout = timeout
        self.interval = interval
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
            params: The query parameters based on UltraOCR Docs, optional in most cases.

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
        """Generate signed url to send the document.

        Generate signed url to send the document to be processed by the AI.

        Args:
            service: The the type of document to be send.
            metadata: The metadata based on UltraOCR Docs format, optional in most cases.
            params: The query parameters based on UltraOCR Docs, optional in most cases.
            resource: The way to process, whether job or batch.

        Returns:
            A json response containing the id, status_url, urls to upload (only "document"if you're
            not using facematch or extra document features) and the expiration time (1 minute).
            For example:
            {
                "exp": "60000",
                "id": "0ujsszwN8NRY24YaXiTIE2VWDTS",
                "status_url": "https://ultraocr.apis.nuveo.ai/v2/ocr/batch/status/0ujsszwN8NRY24YaXiTIE2VWDTS",
                "urls": {
                    "document": "https://presignedurldemo.s3.eu-west-2.amazonaws.com/image.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAJJWZ7B6WCRGMKFGQ%2F20180210%2Feu-west-2%2Fs3%2Faws4_request&X-Amz-Date=20180210T171315Z&X-Amz-Expires=1800&X-Amz-Signature=12b74b0788aa036bc7c3d03b3f20c61f1f91cc9ad8873e3314255dc479a25351&X-Amz-SignedHeaders=host",
                    "selfie": "https://presignedurldemo.s3.eu-west-2.amazonaws.com/image.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAJJWZ7B6WCRGMKFGQ%2F20180210%2Feu-west-2%2Fs3%2Faws4_request&X-Amz-Date=20180210T171315Z&X-Amz-Expires=1800&X-Amz-Signature=12b74b0788aa036bc7c3d03b3f20c61f1f91cc9ad8873e3314255dc479a25351&X-Amz-SignedHeaders=host",
                    "extra_document": "https://presignedurldemo.s3.eu-west-2.amazonaws.com/image.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAJJWZ7B6WCRGMKFGQ%2F20180210%2Feu-west-2%2Fs3%2Faws4_request&X-Amz-Date=20180210T171315Z&X-Amz-Expires=1800&X-Amz-Signature=12b74b0788aa036bc7c3d03b3f20c61f1f91cc9ad8873e3314255dc479a25351&X-Amz-SignedHeaders=host"
                }
            }
        """
        url = f"{self.base_url}/{resource}/{service}"
        resp = requests.post(
            url, auth=self._bearer_token(), json=metadata, params=params
        )
        return resp.json()

    def get_batch_status(self, batch_id: str):
        """Get document batch status.

        Get the status of the batch, checking whether it was processed or not.

        Args:
            batch_id: The id of the batch, given on batch creation.

        Returns:
            A json response containing the id, creation time, batch's jobs info, service and
            status (may be "waiting", "error", "processing" or "done"). For example:
            {
                "batch_ksuid": "2AwrSd7bxEMbPrQ5jZHGDzQ4qL3",
                "created_at": "2022-06-22T20:58:09Z",
                "jobs": [
                    {
                        "created_at": "2022-06-22T20:58:09Z",
                        "job_ksuid": "0ujsszwN8NRY24YaXiTIE2VWDTS",
                        "result_url": "https://ultraocr.apis.nuveo.ai/v2/ocr/job/result/2AwrSd7bxEMbPrQ5jZHGDzQ4qL3/0ujsszwN8NRY24YaXiTIE2VWDTS",
                        "status": "processing"
                    }
                ],
                "service": "cnh",
                "status": "done"
            }
        """
        route = f"{self.base_url}/batch/status/{batch_id}"
        resp = requests.get(route, auth=self._bearer_token())
        return resp.json()

    def get_job_result(self, batch_id: str, job_id: str):
        """Get job result.

        Get the status and result of the job if it's already processed.

        Args:
            batch_id: The id of the batch, given on batch creation(repeat the job_id if batch wasn't created).
            job_id: The id of the job, given on job creation or on batch status.

        Returns:
            A json response containing the client data (if given on job creation), id, creation
            time, service, status (may be "waiting", "error", "processing", "validating" or "done")
            and the result or error depending on the status. For example:
            {
                "client_data": { },
                "created_at": "2022-06-22T20:58:09Z",
                "job_ksuid": "2AwrSd7bxEMbPrQ5jZHGDzQ4qL3",
                "result": {
                    "Time": "7.45",
                    "Document": [
                        {
                            "Page": 1,
                            "Data": {
                                "DocumentType": {
                                    "conf": 99,
                                    "value": "CNH"
                                }
                            }
                        }
                    ]
                },
                "service": "idtypification",
                "status": "done"
            }
        """
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
        """Send job.

        Create and upload a job.

        Args:
            service: The the type of document to be send.
            file_path: The file path of the document.
            metadata: The metadata based on UltraOCR Docs format, optional in most cases.
            params: The query parameters based on UltraOCR Docs, optional in most cases.

        Returns:
            A json response containing the id and the status_url. For example:

            {
                "id": "0ujsszwN8NRY24YaXiTIE2VWDTS",
                "status_url": "https://ultraocr.apis.nuveo.ai/v2/ocr/job/result/0ujsszwN8NRY24YaXiTIE2VWDTS"
            }
        """
        # TODO facematch/extra document
        with open(file_path, "rb") as file_bin:
            data = file_bin.read()

        res = self.generate_signed_url(service, metadata, params, Resource.JOB)
        job_data = {
            "id": res.get("id"),
            "status_url": res.get("status_url"),
        }
        url = res.get("urls", {}).get("document")
        requests.put(url, data=data)
        return job_data

    def send_batch(
        self, service: str, file_path: str, metadata: dict = None, params: dict = None
    ):
        """Send batch.

        Create and upload a batch.

        Args:
            service: The the type of document to be send.
            file_path: The file path of the document.
            metadata: The metadata based on UltraOCR Docs format, optional in most cases.
            params: The query parameters based on UltraOCR Docs, optional in most cases.

        Returns:
            A json response containing the id and the status_url. For example:

            {
                "id": "0ujsszwN8NRY24YaXiTIE2VWDTS",
                "status_url": "https://ultraocr.apis.nuveo.ai/v2/ocr/job/result/0ujsszwN8NRY24YaXiTIE2VWDTS"
            }
        """
        with open(file_path, "rb") as file_bin:
            data = file_bin.read()

        res = self.generate_signed_url(service, metadata, params, Resource.BATCH)
        batch_data = {
            "id": res.get("id"),
            "status_url": res.get("status_url"),
        }
        url = res.get("urls", {}).get("document")
        requests.put(url, data=data)
        return batch_data

    def send_job_base64(
        self,
        service: str,
        file: str,
        metadata: dict = None,
        params: dict = None,
    ):
        """Send job on base64.

        Create and upload a job on base64 format (recommended only if you have already converted
        the file to base64 format).

        Args:
            service: The the type of document to be send.
            file: The file on base64 format.
            metadata: The metadata based on UltraOCR Docs format, optional in most cases.
            params: The query parameters based on UltraOCR Docs, optional in most cases.

        Returns:
            A json response containing the id and the status_url. For example:

            {
                "id": "0ujsszwN8NRY24YaXiTIE2VWDTS",
                "status_url": "https://ultraocr.apis.nuveo.ai/v2/ocr/job/result/0ujsszwN8NRY24YaXiTIE2VWDTS"
            }
        """
        # TODO facematch/extra document
        params = {
            **params,
            "base64": "true",
        }

        res = self.generate_signed_url(service, metadata, params, Resource.JOB)
        job_data = {
            "id": res.get("id"),
            "status_url": res.get("status_url"),
        }
        url = res.get("urls", {}).get("document")
        requests.put(url, data=file)
        return job_data

    def send_batch_base64(
        self,
        service: str,
        file: str,
        metadata: dict = None,
        params: dict = None,
    ):
        """Send batch on base64.

        Create and upload a batch on base64 format (recommended only if you have already converted
        the file to base64 format).

        Args:
            service: The the type of document to be send.
            file: The file on base64 format.
            metadata: The metadata based on UltraOCR Docs format, optional in most cases.
            params: The query parameters based on UltraOCR Docs, optional in most cases.

        Returns:
            A json response containing the id and the status_url. For example:

            {
                "id": "0ujsszwN8NRY24YaXiTIE2VWDTS",
                "status_url": "https://ultraocr.apis.nuveo.ai/v2/ocr/job/result/0ujsszwN8NRY24YaXiTIE2VWDTS"
            }
        """
        params = {
            **params,
            "base64": "true",
        }
        res = self.generate_signed_url(service, metadata, params, Resource.BATCH)
        batch_data = {
            "id": res.get("id"),
            "status_url": res.get("status_url"),
        }

        url = res.get("urls", {}).get("document")
        requests.put(url, data=file)
        return batch_data

    def wait_for_job_done(self, batch_id: str, job_id: str):
        """Wait the job to be processed.

        Wait the job to be processed and returns the result.

        Args:
            batch_id: The id of the batch, given on batch creation(repeat the job_id if batch wasn't created).
            job_id: The id of the job, given on job creation or on batch status.

        Returns:
            A json response containing the client data (if given on job creation), id, creation
            time, service, status (may be "waiting", "error", "processing", "validating" or "done")
            and the result or error depending on the status. For example:
            {
                "client_data": { },
                "created_at": "2022-06-22T20:58:09Z",
                "job_ksuid": "2AwrSd7bxEMbPrQ5jZHGDzQ4qL3",
                "result": {
                    "Time": "7.45",
                    "Document": [
                        {
                            "Page": 1,
                            "Data": {
                                "DocumentType": {
                                    "conf": 99,
                                    "value": "CNH"
                                }
                            }
                        }
                    ]
                },
                "service": "idtypification",
                "status": "done"
            }
        """
        timeout_start = time.time()
        code = None
        res = None

        while time.time() < timeout_start + self.timeout:
            res, code = self.get_job_result(batch_id, job_id)

            status = res["status"]
            if status == "done" or status == "error":
                break

            time.sleep(self.interval)

        if time.time() > timeout_start + self.timeout:
            raise TimeoutException(self.timeout, res)

        return res, code

    def wait_for_batch_done(self, batch_id: str, wait_jobs: bool = True):
        """Wait the batch to be processed.

        Wait the batch to be processed and returns the status. The function will wait the timeout
        given on Client creation.

        Args:
            batch_id: The id of the batch, given on batch creation(repeat the job_id if batch wasn't created).
            wait_jobs: Indicate if must wait the jobs to be processed.

        Returns:
            A json response containing the id, creation time, batch's jobs info, service and
            status (may be "waiting", "error", "processing" or "done"). For example:
            {
                "batch_ksuid": "2AwrSd7bxEMbPrQ5jZHGDzQ4qL3",
                "created_at": "2022-06-22T20:58:09Z",
                "jobs": [
                    {
                        "created_at": "2022-06-22T20:58:09Z",
                        "job_ksuid": "0ujsszwN8NRY24YaXiTIE2VWDTS",
                        "result_url": "https://ultraocr.apis.nuveo.ai/v2/ocr/job/result/2AwrSd7bxEMbPrQ5jZHGDzQ4qL3/0ujsszwN8NRY24YaXiTIE2VWDTS",
                        "status": "processing"
                    }
                ],
                "service": "cnh",
                "status": "done"
            }
        """
        timeout_start = time.time()
        code = None
        res = None

        while time.time() < timeout_start + self.timeout:
            res, code = self.get_batch_status(batch_id)

            status = res["status"]
            if status == "done" or status == "error":
                break

            time.sleep(self.interval)

        if time.time() > timeout_start + self.timeout:
            raise TimeoutException(self.timeout, res)

        if wait_jobs:
            for job in res["jobs"]:
                job_id = job["job_ksuid"]
                self.wait_for_job_done(batch_id, job_id)

        return res, code
