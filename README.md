# UltraOCR SDK Python

UltraOCR SDK for Python.

[UltraOCR](https://ultraocr.com.br/) is a platform that assists in the document analysis process with AI.

For more details about the system, types of documents, routes and params, access our [documentation](https://docs.nuveo.ai/ocr/v2/).

## Instalation

First of all, you must install this package with pip:

```
pip install git+https://github.com/nuveo/ultraocr-sdk-python
```

Then you must import the UltraOCR SDK in your code , with:

```python
import ultraocr
```

Or:

```python
from ultraocr import Client
```

## Step by step

### First step - Client Creation and Authentication

With the UltraOCR SDK installed and imported, the first step is create the Client and authenticate, you have two ways to do it.

The first one, you can do it in two steps with:

```python
from ultraocr import Client

client = Client()
client.authenticate("YOUR_CLIENT_ID", "YOUR_CLIENT_SECRET")
```

Optionally, you can pass a third argument `expires` on `authenticate` function, a number between `1` and `1440`, the Token time expiration in minutes. The default value is 60.

Another way is creating the client with the Client info and `auto_refresh` as `True`. As example:

```python
from ultraocr import Client

client = Client(client_id="YOUR_CLIENT_ID", client_secret="YOUR_CLIENT_SECRET", auto_refresh=True)
```

The Client have following allowed parameters:

* `client_id`: The Client ID to generate token (only if `auto_refresh=True`).
* `client_secret`: The Client Secret to generate token (only if `auto_refresh=True`).
* `token_expires`: The token expiration time (only if `auto_refresh=True`) (Default 60).
* `auto_refresh`: Indicates that the token will be auto generated (with `client_id`, `client_secret` and `token_expires` parameters) (Default False).
* `auth_base_url`: The base url to authenticate (Default UltraOCR url).
* `base_url`: The base url to send documents (Default UltraOCR url).
* `timeout`: The pooling timeout in seconds (Default 30).
* `interval`: The pooling interval in seconds (Default 1).


### Second step - Send Documents

With everything set up, you can send documents: 

```python
client.send_job("SERVICE", "FILE_PATH") # Simple job
client.send_batch("SERVICE", "FILE_PATH") # Simple batch
client.send_job_base64("SERVICE", "BASE64_DATA") # Job in base64
client.send_batch_base64("SERVICE", "BASE64_DATA") # Batch in base64
client.send_job_single_step("SERVICE", "BASE64_DATA") # Job in base64, faster, but with limits
```

Send batch response example:

```json
{
    "id": "0ujsszwN8NRY24YaXiTIE2VWDTS",
    "status_url": "https://ultraocr.apis.nuveo.ai/v2/ocr/batch/status/0ujsszwN8NRY24YaXiTIE2VWDTS"
}
```

Send job response example:

```json
{
    "id": "0ujsszwN8NRY24YaXiTIE2VWDTS",
    "status_url": "https://ultraocr.apis.nuveo.ai/v2/ocr/job/result/0ujsszwN8NRY24YaXiTIE2VWDTS"
}
```

In every above utilities you can send metadata and query params with `metadata` and `params` respectively dict parameters.

For jobs, to send facematch file (if you requested on query params or using facematch service), you must provide `facematch_file` on `send_job_base64` and `send_job_single_step` or `facematch_file_path` on `send_job`. To send extra file (if you requested on query params) with document back side, you must provide `extra_file` on `send_job_base64` and `send_job_single_step` or `extra_file_path` on `send_job`.

Examples using CNH service and sending facematch and extra files:

```python
params = {
    "extra-document": "true",
    "facematch": "true"
}

client.send_job("cnh", "FILE_PATH", facematch_file_path="FACEMATCH_FILE_PATH", extra_file_path="EXTRA_FILE_PATH", params=params)
client.send_job_base64("SERVICE", "BASE64_DATA", facematch_file="FACEMATCH_BASE64_DATA", extra_file="EXTRA_BASE64_DATA", params=params)
client.send_job_single_step("SERVICE", "BASE64_DATA", facematch_file="FACEMATCH_BASE64_DATA", extra_file="EXTRA_BASE64_DATA", params=params)
```

Alternatively, you can request the signed url directly, without any utility, but you will must to upload the document manually. Example:

```python
import requests
from ultraocr import Client, Resource

res = client.generate_signed_url("SERVICE") # Request job
urls = res.get("urls", {})
url = urls.get("document")

with open("FILE_PATH", "rb") as file_bin:
    data = file_bin.read()

resp = requests.put(url, data=data)

res = client.generate_signed_url("SERVICE", resource=Resource.BATCH) # Request batch
urls = res.get("urls", {})
url = urls.get("document")

with open("FILE_PATH", "rb") as file_bin:
    data = file_bin.read()

resp = requests.put(url, data=data)
```

Example of response from `generate_signed_url` with facematch and extra files:

```json
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
```

### Third step - Get Result

With the job or batch id, you can get the job result or batch status with:

```python
client.get_batch_status("BATCH_ID") # Batches
client.get_job_result("JOB_ID", "JOB_ID") # Simple jobs
client.get_job_result("BATCH_ID", "JOB_ID") # Jobs belonging to batches
```

Alternatively, you can use a utily `wait_for_job_done` or `wait_for_batch_done`:

```python
client.wait_for_batch_done("BATCH_ID") # Batches, ends when the batch and all it jobs are finished
client.wait_for_batch_done("BATCH_ID", wait_jobs=False) # Batches, ends when the batch is finished
client.wait_for_job_done("JOB_ID", "JOB_ID") # Simple jobs
client.wait_for_job_done("BATCH_ID", "JOB_ID") # Jobs belonging to batches
```

Batch status example:

```json
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
```

Job result example:

```json
{
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
```

### Simplified way

You can do all steps in a simplified way, with `create_and_wait_job` or `create_and_wait_batch` utilities:

```python
from ultraocr import Client

client = Client(client_id="YOUR_CLIENT_ID", client_secret="YOUR_CLIENT_SECRET", auto_refresh=True)
client.create_and_wait_job(service="SERVICE", file_path="YOUR_FILE_PATH")
```

Or:

```python
from ultraocr import Client

client = Client(client_id="YOUR_CLIENT_ID", client_secret="YOUR_CLIENT_SECRET", auto_refresh=True)
client.create_and_wait_batch(service="SERVICE", file_path="YOUR_FILE_PATH")
```

The `create_and_wait_job` has the `send_job` arguments and `get_job_result` response, while the `create_and_wait_batch` has the `send_batch` arguments and `get_batch_status` response. 