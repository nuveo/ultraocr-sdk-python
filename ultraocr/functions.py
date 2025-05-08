""" Module providing the UltraOCR Client and functions """

import time
from http import HTTPStatus
from datetime import datetime, timedelta

import requests

from ultraocr.helpers import (
    BearerAuth,
    upload_file,
    upload_file_with_path,
    validate_status_code,
)
from ultraocr.exceptions import TimeoutException
from ultraocr.constants import (
    Resource,
    POOLING_INTERVAL,
    API_TIMEOUT,
    BASE_URL,
    AUTH_BASE_URL,
    DEFAULT_EXPIRATION_TIME,
    STATUS_DONE,
    STATUS_ERROR,
    FLAG_TRUE,
    KEY_EXTRA,
    KEY_FACEMATCH,
    RETURN_REQUEST,
    RETURN_STORAGE,
)


class Client:
    """UltraOCR Client

    Client to help on UltraOCR usage. For more details about all arguments and returns,
    access the oficial system documentation on https://docs.nuveo.ai/ocr/v2/.

    Attributes:
        client_id: The Client ID to generate token (only if auto_refresh=True).
        client_secret: The Client Secret to generate token (only if auto_refresh=True).
        token_expires: The token expiration time (only if auto_refresh=True).
        auto_refresh: Indicates that the token will be auto generated (with client_id, client_secret and token_expires parameters).
        auth_base_url: The base url to authenticate.
        base_url: The base url to send documents.
        timeout: The pooling timeout.
        interval: The pooling interval.
        expires_at: The authentication token expires datetime.
        token: The authentication token.

    """

    def __init__(
        self,
        client_id: str = "",
        client_secret: str = "",
        token_expires: int = DEFAULT_EXPIRATION_TIME,
        auto_refresh: bool = False,
        auth_base_url: str = AUTH_BASE_URL,
        base_url: str = BASE_URL,
        timeout: int = API_TIMEOUT,
        interval: int = POOLING_INTERVAL,
    ):
        """Initializes the instance based on preferences.

        Args:
            client_id: The Client ID to generate token (only if auto_refresh=True).
            client_secret: The Client Secret to generate token (only if auto_refresh=True).
            token_expires: The token expiration time (only if auto_refresh=True) (Default 60).
            auto_refresh: Indicates that the token will be auto generated (with client_id, client_secret and token_expires parameters) (Default False).
            auth_base_url: The base url to authenticate (Default official UltraOCR URL).
            base_url: The base url to send documents (Default official UltraOCR URL).
            timeout: The pooling timeout in seconds (Default 30).
            interval: The pooling interval in seconds (Default 1).
        """
        self.auth_base_url = auth_base_url
        self.base_url = base_url
        self.timeout = timeout
        self.interval = interval
        self.client_id = client_id
        self.client_secret = client_secret
        self.auto_refresh = auto_refresh
        self.expires = token_expires
        self.expires_at = datetime.now()
        self.token = ""

    def _bearer_token(self):
        return BearerAuth(self.token)

    def _post(
        self,
        url: str,
        json: dict = None,
        params: dict = None,
        timeout: int = API_TIMEOUT,
    ):
        self._auto_authenticate()

        return requests.post(
            url,
            auth=self._bearer_token(),
            json=json,
            params=params,
            timeout=timeout,
        )

    def _get(
        self,
        url: str,
        params: dict = None,
        timeout: int = API_TIMEOUT,
    ):
        self._auto_authenticate()

        return requests.get(
            url,
            auth=self._bearer_token(),
            params=params,
            timeout=timeout,
        )

    def _auto_authenticate(self) -> None:
        if self.auto_refresh and datetime.now() > self.expires_at:
            self.authenticate(self.client_id, self.client_secret, self.expires)

    def _get_batch_result(self, batch_id: str, params: dict = None):
        url = f"{self.base_url}/ocr/batch/result/{batch_id}"

        resp = self._get(url, params=params)
        validate_status_code(resp.status_code, HTTPStatus.OK)

        return resp.json()

    def authenticate(
        self, client_id: str, client_secret: str, expires: int = DEFAULT_EXPIRATION_TIME
    ) -> None:
        """Authenticate on UltraOCR.

        Authenticate on UltraOCR and save the token to use on future requests.

        Args:
            client_id: The Client ID generated on Web Interface.
            client_secret: The Client Secret generated on Web Interface.
            expires: The token expires time in minutes (Default 60).

        Raises:
            InvalidStatusCodeException: If status code is not 200.
        """
        url = f"{self.auth_base_url}/token"
        data = {
            "ClientID": client_id,
            "ClientSecret": client_secret,
            "ExpiresIn": expires,
        }

        resp = requests.post(url, json=data, timeout=API_TIMEOUT)
        validate_status_code(resp.status_code, HTTPStatus.OK)

        self.token = resp.json()["token"]
        self.expires_at = datetime.now() + timedelta(minutes=expires)

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
            service: The the type of document to be sent.
            metadata: The metadata based on UltraOCR Docs format, optional in most cases.
            params: The query parameters based on UltraOCR Docs, optional in most cases.
            resource: The way to process, whether job or batch (Default job).

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

        Raises:
            InvalidStatusCodeException: If status code is not 200.
        """
        url = f"{self.base_url}/ocr/{resource.value}/{service}"

        resp = self._post(url, json=metadata, params=params)
        validate_status_code(resp.status_code, HTTPStatus.OK)

        return resp.json()

    def send_job_single_step(
        self,
        service: str,
        file: str,
        facematch_file: str = "",
        extra_file: str = "",
        metadata: dict = None,
        params: dict = None,
    ):
        """Send job in a single step on UltraOCR.

        Send job in a single step on UltraOCR, it's faster than usual method,
        but have a 6MB as body limit (including metadata and base64 file)

        Args:
            service: The the type of document to be sent.
            file: The file in base64 format.
            facematch_file: The facematch file in base64 format.
            extra_file: The extra file in base64 format.
            metadata: The metadata based on UltraOCR Docs format, optional in most cases.
            params: The query parameters based on UltraOCR Docs, optional in most cases.

        Returns:
            A json response containing the id and the status_url. For example:

            {
                "id": "0ujsszwN8NRY24YaXiTIE2VWDTS",
                "status_url": "https://ultraocr.apis.nuveo.ai/v2/ocr/job/result/0ujsszwN8NRY24YaXiTIE2VWDTS"
            }

        Raises:
            InvalidStatusCodeException: If status code is not 200.
        """
        if metadata is None:
            metadata = {}

        url = f"{self.base_url}/ocr/job/send/{service}"
        body = {
            "metadata": metadata,
            "data": file,
        }

        if params and params.get(KEY_FACEMATCH) == FLAG_TRUE:
            body.update(KEY_FACEMATCH, facematch_file)

        if params and params.get(KEY_EXTRA) == FLAG_TRUE:
            body.update("extra", extra_file)

        resp = self._post(url, json=body, params=params)
        validate_status_code(resp.status_code, HTTPStatus.OK)

        return resp.json()

    def send_job(
        self,
        service: str,
        file_path: str,
        facematch_file_path: str = "",
        extra_file_path: str = "",
        metadata: dict = None,
        params: dict = None,
    ):
        """Send job.

        Create and upload a job.

        Args:
            service: The the type of document to be sent.
            file_path: The file path of the document.
            facematch_file_path: The facematch file path of the document.
            extra_file_path: The extra file path of the document.
            metadata: The metadata based on UltraOCR Docs format, optional in most cases.
            params: The query parameters based on UltraOCR Docs, optional in most cases.

        Returns:
            A json response containing the id and the status_url. For example:

            {
                "id": "0ujsszwN8NRY24YaXiTIE2VWDTS",
                "status_url": "https://ultraocr.apis.nuveo.ai/v2/ocr/job/result/0ujsszwN8NRY24YaXiTIE2VWDTS"
            }

        Raises:
            InvalidStatusCodeException: If status code is not 200.
        """
        res = self.generate_signed_url(service, metadata, params, Resource.JOB)
        urls = res.get("urls", {})
        job_data = {
            "id": res.get("id"),
            "status_url": res.get("status_url"),
        }

        url = urls.get("document")
        upload_file_with_path(url, file_path)

        if params and params.get(KEY_FACEMATCH) == FLAG_TRUE:
            facematch_url = urls.get("selfie")
            upload_file_with_path(facematch_url, facematch_file_path)

        if params and params.get(KEY_EXTRA) == FLAG_TRUE:
            extra_url = urls.get("extra_document")
            upload_file_with_path(extra_url, extra_file_path)

        return job_data

    def send_batch(
        self, service: str, file_path: str, metadata: list[dict] = None, params: dict = None
    ):
        """Send batch.

        Create and upload a batch.

        Args:
            service: The the type of document to be sent.
            file_path: The file path of the document.
            metadata: The metadata based on UltraOCR Docs format, optional in most cases.
            params: The query parameters based on UltraOCR Docs, optional in most cases.

        Returns:
            A json response containing the id and the status_url. For example:

            {
                "id": "0ujsszwN8NRY24YaXiTIE2VWDTS",
                "status_url": "https://ultraocr.apis.nuveo.ai/v2/ocr/batch/status/0ujsszwN8NRY24YaXiTIE2VWDTS"
            }

        Raises:
            InvalidStatusCodeException: If status code is not 200.
        """
        res = self.generate_signed_url(service, metadata, params, Resource.BATCH)
        url = res.get("urls", {}).get("document")
        batch_data = {
            "id": res.get("id"),
            "status_url": res.get("status_url"),
        }

        upload_file_with_path(url, file_path)

        return batch_data

    def send_job_base64(
        self,
        service: str,
        file: str,
        facematch_file: str = "",
        extra_file: str = "",
        metadata: dict = None,
        params: dict = None,
    ):
        """Send job on base64.

        Create and upload a job on base64 format (recommended only if you have already converted
        the file to base64 format).

        Args:
            service: The the type of document to be sent.
            file: The file on base64 format.
            facematch_file: The facematch file in base64 format.
            extra_file: The extra file in base64 format.
            metadata: The metadata based on UltraOCR Docs format, optional in most cases.
            params: The query parameters based on UltraOCR Docs, optional in most cases.

        Returns:
            A json response containing the id and the status_url. For example:

            {
                "id": "0ujsszwN8NRY24YaXiTIE2VWDTS",
                "status_url": "https://ultraocr.apis.nuveo.ai/v2/ocr/job/result/0ujsszwN8NRY24YaXiTIE2VWDTS"
            }

        Raises:
            InvalidStatusCodeException: If status code is not 200.
        """
        if params is None:
            params = {}

        params = {
            **params,
            "base64": FLAG_TRUE,
        }

        res = self.generate_signed_url(service, metadata, params, Resource.JOB)
        urls = res.get("urls", {})
        job_data = {
            "id": res.get("id"),
            "status_url": res.get("status_url"),
        }

        url = urls.get("document")
        upload_file(url, file)

        if params and params.get(KEY_FACEMATCH) == FLAG_TRUE:
            facematch_url = urls.get("selfie")
            upload_file(facematch_url, facematch_file)

        if params and params.get(KEY_EXTRA) == FLAG_TRUE:
            extra_url = urls.get("extra_document")
            upload_file(extra_url, extra_file)

        return job_data

    def send_batch_base64(
        self,
        service: str,
        file: str,
        metadata: list[dict] = None,
        params: dict = None,
    ):
        """Send batch on base64.

        Create and upload a batch on base64 format (recommended only if you have already converted
        the file to base64 format).

        Args:
            service: The the type of document to be sent.
            file: The file on base64 format.
            metadata: The metadata based on UltraOCR Docs format, optional in most cases.
            params: The query parameters based on UltraOCR Docs, optional in most cases.

        Returns:
            A json response containing the id and the status_url. For example:

            {
                "id": "0ujsszwN8NRY24YaXiTIE2VWDTS",
                "status_url": "https://ultraocr.apis.nuveo.ai/v2/ocr/batch/status/0ujsszwN8NRY24YaXiTIE2VWDTS"
            }

        Raises:
            InvalidStatusCodeException: If status code is not 200.
        """
        if params is None:
            params = {}

        params = {
            **params,
            "base64": FLAG_TRUE,
        }

        res = self.generate_signed_url(service, metadata, params, Resource.BATCH)
        url = res.get("urls", {}).get("document")
        batch_data = {
            "id": res.get("id"),
            "status_url": res.get("status_url"),
        }

        upload_file(url, file)

        return batch_data

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

        Raises:
            InvalidStatusCodeException: If status code is not 200.
        """
        url = f"{self.base_url}/ocr/batch/status/{batch_id}"

        resp = self._get(url)
        validate_status_code(resp.status_code, HTTPStatus.OK)

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

        Raises:
            InvalidStatusCodeException: If status code is not 200.
        """
        url = f"{self.base_url}/ocr/job/result/{batch_id}/{job_id}"

        resp = self._get(url)
        validate_status_code(resp.status_code, HTTPStatus.OK)

        return resp.json()

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

        Raises:
            InvalidStatusCodeException: If status code is not 200.
            TimeoutException: If wait time exceed the limit.
        """
        timeout_start = time.time()
        res = None

        while time.time() < timeout_start + self.timeout:
            res = self.get_job_result(batch_id, job_id)

            status = res["status"]
            if status in [STATUS_DONE, STATUS_ERROR]:
                break

            time.sleep(self.interval)

        if time.time() > timeout_start + self.timeout:
            raise TimeoutException(self.timeout, res)

        return res

    def wait_for_batch_done(self, batch_id: str, wait_jobs: bool = True):
        """Wait the batch to be processed.

        Wait the batch to be processed and returns the status. The function will wait the timeout
        given on Client creation.

        Args:
            batch_id: The id of the batch, given on batch creation.
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

        Raises:
            InvalidStatusCodeException: If status code is not 200.
            TimeoutException: If wait time exceed the limit.
        """
        timeout_start = time.time()
        res = None

        while time.time() < timeout_start + self.timeout:
            res = self.get_batch_status(batch_id)

            status = res["status"]
            if status in [STATUS_DONE, STATUS_ERROR]:
                break

            time.sleep(self.interval)

        if time.time() > timeout_start + self.timeout:
            raise TimeoutException(self.timeout, res)

        if wait_jobs:
            for job in res["jobs"]:
                job_id = job["job_ksuid"]
                self.wait_for_job_done(batch_id, job_id)

        return res

    def get_jobs(self, start: str, end: str) -> list:
        """Get jobs.

        Get all created jobs in a time interval

        Args:
            start: The start time (in the format YYYY-MM-DD).
            end: The end time (in the format YYYY-MM-DD).

        Returns:
            A list of jobs. For example:
            [
                {
                    "created_at": "2021-01-01T00:00:00Z",
                    "job_ksuid": "21eRubs77luzFr1GdJfHdddH6EA",
                    "result": {},
                    "service": "chn",
                    "status": "done"
                }
            ],

        Raises:
            InvalidStatusCodeException: If status code is not 200.
            TimeoutException: If wait time exceed the limit.
        """
        url = f"{self.base_url}/ocr/job/results"
        params = {
            "startDate": start,
            "endtDate": end,
        }

        jobs = []
        has_next_page = True
        while has_next_page:
            resp = self._get(url, params=params)
            res = resp.json()

            jobs += res.get("jobs")
            token = res.get("nextPageToken")

            params.update("nextPageToken", token)

            if not token:
                has_next_page = False

        return jobs

    def create_and_wait_job(
        self,
        service: str,
        file_path: str,
        facematch_file_path: str = "",
        extra_file_path: str = "",
        metadata: dict = None,
        params: dict = None,
    ):
        """Create and wait job.

        Create the job and wait for job done.

        Args:
            service: The the type of document to be sent.
            file_path: The file path of the document.
            facematch_file_path: The facematch file path of the document.
            extra_file_path: The extra file path of the document.
            metadata: The metadata based on UltraOCR Docs format, optional in most cases.
            params: The query parameters based on UltraOCR Docs, optional in most cases.

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

        Raises:
            InvalidStatusCodeException: If status code is not 200.
            TimeoutException: If wait time exceed the limit.
        """

        res = self.send_job(
            service, file_path, facematch_file_path, extra_file_path, metadata, params
        )

        job_id = res.get("id")

        return self.wait_for_job_done(job_id, job_id)

    def create_and_wait_batch(
        self,
        service: str,
        file_path: str,
        metadata: list[dict] = None,
        params: dict = None,
        wait_jobs: bool = True,
    ):
        """Create and wait batch.

        Create the batch and wait for batch done.

        Args:
            service: The the type of document to be sent.
            file_path: The file path of the document.
            metadata: The metadata based on UltraOCR Docs format, optional in most cases.
            params: The query parameters based on UltraOCR Docs, optional in most cases.
            wait_jobs: Indicate if must wait the jobs to be processed (Default True).

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

        Raises:
            InvalidStatusCodeException: If status code is not 200.
            TimeoutException: If wait time exceed the limit.
        """

        res = self.send_batch(service, file_path, metadata, params)

        batch_id = res.get("id")

        return self.wait_for_batch_done(batch_id, wait_jobs)

    def get_job_info(self, job_id: str):
        """Get job info.

        Get the info with more details.

        Args:
            job_id: The id of the job, given on job creation or on batch status.

        Returns:
            A json response containing the client data (if given on job creation), the metadata (if
            given on job creation), job id, company id, client id creation time, service, source,
            status (may be "waiting", "error", "processing", "validating" or "done") and the result
            or error depending on the status. For example:
            {
                "client_data": { },
                "metadata": { },
                "created_at": "2022-06-22T20:58:09Z",
                "company_id": "123",
                "client_id": "1234",
                "job_id": "2AwrSd7bxEMbPrQ5jZHGDzQ4qL3",
                "source": "API",
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

        Raises:
            InvalidStatusCodeException: If status code is not 200.
        """
        url = f"{self.base_url}/ocr/job/info/{job_id}"

        resp = self._get(url)
        validate_status_code(resp.status_code, HTTPStatus.OK)

        return resp.json()
    
    def get_batch_info(self, batch_id: str):
        """Get document batch info.

        Get the info of the batch with more details, checking whether it was processed or not.

        Args:
            batch_id: The id of the batch, given on batch creation.

        Returns:
            A json response containing the id, company id, client id, creation time, service,
            source, number of jobs, number of processed jobs and status (may be "waiting", "error",
            "processing" or "done"). For example:
            {
                "company_id": "123",
                "client_id": "1234",
                "batch_id": "2AwrSd7bxEMbPrQ5jZHGDzQ4qL3",
                "created_at": "2022-06-22T20:58:09Z",
                "service": "cnh",
                "status": "done",
                "source": "API",
                "total_jobs": 3,
                "total_processed": 2,
            }

        Raises:
            InvalidStatusCodeException: If status code is not 200.
        """
        url = f"{self.base_url}/ocr/batch/info/{batch_id}"

        resp = self._get(url)
        validate_status_code(resp.status_code, HTTPStatus.OK)

        return resp.json()
    
    def get_batch_result(self, batch_id: str):
        """Get batch jobs results.

        Get the batch jobs results as array.

        Args:
            batch_id: The id of the batch, given on batch creation.

        Returns:
            A json response containing the url to download and the expiration time (1 minute).
            For example:
            [
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
                    "status": "done",
                    "filename": "123.jpg"
                }
            ]

        Raises:
            InvalidStatusCodeException: If status code is not 200.
        """
        params = {
            "return": RETURN_REQUEST,
        }

        return self._get_batch_result(batch_id, params)
    
    def get_batch_result_storage(self, batch_id: str, params: dict = None):
        """Get batch jobs results as file.

        Generate url to download a file containing the batch jobs results.

        Args:
            batch_id: The id of the batch, given on batch creation.
            params: The query parameters based on UltraOCR Docs.

        Returns:
            A json response containing the url to download and the expiration time (1 minute).
            For example:
            {
                "exp": "60000",
                "url": "https://presignedurldemo.s3.eu-west-2.amazonaws.com/image.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAJJWZ7B6WCRGMKFGQ%2F20180210%2Feu-west-2%2Fs3%2Faws4_request&X-Amz-Date=20180210T171315Z&X-Amz-Expires=1800&X-Amz-Signature=12b74b0788aa036bc7c3d03b3f20c61f1f91cc9ad8873e3314255dc479a25351&X-Amz-SignedHeaders=host"
            }

        Raises:
            InvalidStatusCodeException: If status code is not 200.
        """
        if params is None:
            params = {}

        params = {
            **params,
            "return": RETURN_STORAGE,
        }

        return self._get_batch_result(batch_id, params)