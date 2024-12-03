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

With everything set up, you can send documents.

### Third step - Get Result

With the job or batch id, you can get the job result or batch status with:

```python
client.get_batch_status("BATCH_ID") # Batches
client.get_job_result("JOB_ID", "JOB_ID") # Simple jobs
client.get_job_result("BATCH_ID", "JOB_ID") # Jobs belonging to batches
```

Alternatively, you can use a utily `wait_for_job_done` or `wait_for_batch_done`:

```python
client.wait_for_batch_done("BATCH_ID") # Batches, ends when the batch is finished
client.wait_for_batch_done("BATCH_ID", wait_jobs=True) # Batches, ends when all batch jobs are finisheds.
client.wait_for_job_done("JOB_ID", "JOB_ID") # Simple jobs
client.wait_for_job_done("BATCH_ID", "JOB_ID") # Jobs belonging to batches
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