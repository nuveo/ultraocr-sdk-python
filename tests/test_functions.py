import unittest, responses

from ultraocr import (
    Client,
    BASE_URL,
    AUTH_BASE_URL,
    InvalidStatusCodeException,
    TimeoutException,
)


@responses.activate
def test_authenticate():
    responses.add(
        responses.POST,
        f"{AUTH_BASE_URL}/token",
        json={"token": "abc"},
        status=200,
    )

    c = Client()
    c.authenticate("123", "321")


@responses.activate
def test_authenticate_unauthorized():
    responses.add(
        responses.POST,
        f"{AUTH_BASE_URL}/token",
        status=401,
    )

    c = Client()
    unittest.TestCase().assertRaises(
        InvalidStatusCodeException, c.authenticate, "123", "321"
    )


@responses.activate
def test_generate_signed_url():
    responses.add(
        responses.POST,
        f"{BASE_URL}/ocr/job/rg",
        json={
            "urls": {"document": "https://test2.com"},
            "id": "123",
            "status_url": "https://test.com",
        },
        status=200,
    )

    c = Client()
    res = c.generate_signed_url("rg")

    assert res.get("id")
    assert res.get("status_url")
    assert res.get("urls")

    assert res.get("id") == "123"
    assert res.get("status_url") == "https://test.com"


@responses.activate
def test_generate_signed_url_unauthorized():
    responses.add(
        responses.POST,
        f"{BASE_URL}/ocr/job/rg",
        status=401,
    )

    c = Client()
    unittest.TestCase().assertRaises(
        InvalidStatusCodeException, c.generate_signed_url, "rg"
    )


@responses.activate
def test_get_batch_status():
    responses.add(
        responses.GET,
        f"{BASE_URL}/ocr/batch/status/123",
        json={
            "batch_ksuid": "123",
            "jobs": [],
            "service": "rg",
            "status": "processing",
        },
        status=200,
    )

    c = Client()
    res = c.get_batch_status("123")

    assert res.get("batch_ksuid")
    assert len(res.get("jobs")) == 0
    assert res.get("service")
    assert res.get("status")

    assert res.get("batch_ksuid") == "123"
    assert res.get("service") == "rg"
    assert res.get("status") == "processing"


@responses.activate
def test_get_batch_status_unauthorized():
    responses.add(
        responses.GET,
        f"{BASE_URL}/ocr/batch/status/123",
        status=401,
    )

    c = Client()
    unittest.TestCase().assertRaises(
        InvalidStatusCodeException, c.get_batch_status, "123"
    )


@responses.activate
def test_get_job_result():
    responses.add(
        responses.GET,
        f"{BASE_URL}/ocr/job/result/123/123",
        json={
            "job_ksuid": "123",
            "result": {
                "Time": "7.45",
                "Document": [
                    {"Page": 1, "Data": {"DocumentType": {"conf": 99, "value": "CNH"}}}
                ],
            },
            "service": "rg",
            "status": "done",
        },
        status=200,
    )

    c = Client()
    res = c.get_job_result("123", "123")

    assert res.get("job_ksuid")
    assert res.get("result")
    assert res.get("service")
    assert res.get("status")

    assert res.get("job_ksuid") == "123"
    assert res.get("service") == "rg"
    assert res.get("status") == "done"


@responses.activate
def test_get_job_result_unauthorized():
    responses.add(
        responses.GET,
        f"{BASE_URL}/ocr/job/result/123/123",
        status=401,
    )

    c = Client()
    unittest.TestCase().assertRaises(
        InvalidStatusCodeException, c.get_job_result, "123", "123"
    )


@responses.activate
def test_send_job_single_step():
    responses.add(
        responses.POST,
        f"{BASE_URL}/ocr/job/send/rg",
        json={
            "id": "123",
            "status_url": "https://test.com",
        },
        status=200,
    )

    c = Client()
    res = c.send_job_single_step("rg", "aaa")

    assert res.get("id")
    assert res.get("status_url")

    assert res.get("id") == "123"
    assert res.get("status_url") == "https://test.com"


@responses.activate
def test_send_job_single_step_unauthorized():
    responses.add(
        responses.POST,
        f"{BASE_URL}/ocr/job/send/rg",
        status=401,
    )

    c = Client()
    unittest.TestCase().assertRaises(
        InvalidStatusCodeException, c.send_job_single_step, "rg", "aaa"
    )


@responses.activate
def test_send_job():
    responses.add(
        responses.POST,
        f"{BASE_URL}/ocr/job/rg",
        json={
            "urls": {"document": "https://test2.com"},
            "id": "123",
            "status_url": "https://test.com",
        },
        status=200,
    )

    responses.add(
        responses.PUT,
        "https://test2.com",
        status=200,
    )

    c = Client()
    res = c.send_job("rg", "./requirements.txt")

    assert res.get("id")
    assert res.get("status_url")

    assert res.get("id") == "123"
    assert res.get("status_url") == "https://test.com"


@responses.activate
def test_send_job_invalid_file():
    responses.add(
        responses.POST,
        f"{BASE_URL}/ocr/job/rg",
        json={
            "urls": {"document": "https://test2.com"},
            "id": "123",
            "status_url": "https://test.com",
        },
        status=200,
    )

    responses.add(
        responses.PUT,
        "https://test2.com",
        status=200,
    )

    c = Client()
    unittest.TestCase().assertRaises(Exception, c.send_job, "rg", "requirementss")


@responses.activate
def test_send_job_unauthorized():
    responses.add(
        responses.POST,
        f"{BASE_URL}/ocr/job/rg",
        status=401,
    )

    c = Client()
    unittest.TestCase().assertRaises(
        InvalidStatusCodeException, c.send_job, "rg", "aaa"
    )


@responses.activate
def test_send_job_unauthorized_upload():
    responses.add(
        responses.POST,
        f"{BASE_URL}/ocr/job/rg",
        json={
            "urls": {"document": "https://test2.com"},
            "id": "123",
            "status_url": "https://test.com",
        },
        status=200,
    )

    responses.add(
        responses.PUT,
        "https://test2.com",
        status=401,
    )

    c = Client()
    unittest.TestCase().assertRaises(
        InvalidStatusCodeException, c.send_job, "rg", "./requirements.txt"
    )


@responses.activate
def test_send_job_base64():
    responses.add(
        responses.POST,
        f"{BASE_URL}/ocr/job/rg",
        json={
            "urls": {"document": "https://test2.com"},
            "id": "123",
            "status_url": "https://test.com",
        },
        status=200,
    )

    responses.add(
        responses.PUT,
        "https://test2.com",
        status=200,
    )

    c = Client()
    res = c.send_job_base64("rg", "aaa")

    assert res.get("id")
    assert res.get("status_url")

    assert res.get("id") == "123"
    assert res.get("status_url") == "https://test.com"


@responses.activate
def test_send_job_base64_unauthorized():
    responses.add(
        responses.POST,
        f"{BASE_URL}/ocr/job/rg",
        status=401,
    )

    c = Client()
    unittest.TestCase().assertRaises(
        InvalidStatusCodeException, c.send_job_base64, "rg", "aaa"
    )


@responses.activate
def test_send_job_base64_unauthorized_upload():
    responses.add(
        responses.POST,
        f"{BASE_URL}/ocr/job/rg",
        json={
            "urls": {"document": "https://test2.com"},
            "id": "123",
            "status_url": "https://test.com",
        },
        status=200,
    )

    responses.add(
        responses.PUT,
        "https://test2.com",
        status=401,
    )

    c = Client()
    unittest.TestCase().assertRaises(
        InvalidStatusCodeException, c.send_job_base64, "rg", "aaa"
    )


@responses.activate
def test_send_batch():
    responses.add(
        responses.POST,
        f"{BASE_URL}/ocr/batch/rg",
        json={
            "urls": {"document": "https://test2.com"},
            "id": "123",
            "status_url": "https://test.com",
        },
        status=200,
    )

    responses.add(
        responses.PUT,
        "https://test2.com",
        status=200,
    )

    c = Client()
    res = c.send_batch("rg", "./requirements.txt")

    assert res.get("id")
    assert res.get("status_url")

    assert res.get("id") == "123"
    assert res.get("status_url") == "https://test.com"


@responses.activate
def test_send_batch_invalid_file():
    responses.add(
        responses.POST,
        f"{BASE_URL}/ocr/batch/rg",
        json={
            "urls": {"document": "https://test2.com"},
            "id": "123",
            "status_url": "https://test.com",
        },
        status=200,
    )

    responses.add(
        responses.PUT,
        "https://test2.com",
        status=200,
    )

    c = Client()
    unittest.TestCase().assertRaises(Exception, c.send_batch, "rg", "requirementss")


@responses.activate
def test_send_batch_unauthorized():
    responses.add(
        responses.POST,
        f"{BASE_URL}/ocr/batch/rg",
        status=401,
    )

    c = Client()
    unittest.TestCase().assertRaises(
        InvalidStatusCodeException, c.send_batch, "rg", "aaa"
    )


@responses.activate
def test_send_batch_unauthorized_upload():
    responses.add(
        responses.POST,
        f"{BASE_URL}/ocr/batch/rg",
        json={
            "urls": {"document": "https://test2.com"},
            "id": "123",
            "status_url": "https://test.com",
        },
        status=200,
    )

    responses.add(
        responses.PUT,
        "https://test2.com",
        status=401,
    )

    c = Client()
    unittest.TestCase().assertRaises(
        InvalidStatusCodeException, c.send_batch, "rg", "./requirements.txt"
    )


@responses.activate
def test_send_batch_base64():
    responses.add(
        responses.POST,
        f"{BASE_URL}/ocr/batch/rg",
        json={
            "urls": {"document": "https://test2.com"},
            "id": "123",
            "status_url": "https://test.com",
        },
        status=200,
    )

    responses.add(
        responses.PUT,
        "https://test2.com",
        status=200,
    )

    c = Client()
    res = c.send_batch_base64("rg", "aaa")

    assert res.get("id")
    assert res.get("status_url")

    assert res.get("id") == "123"
    assert res.get("status_url") == "https://test.com"


@responses.activate
def test_send_batch_base64_unauthorized():
    responses.add(
        responses.POST,
        f"{BASE_URL}/ocr/batch/rg",
        status=401,
    )

    c = Client()
    unittest.TestCase().assertRaises(
        InvalidStatusCodeException, c.send_batch_base64, "rg", "aaa"
    )


@responses.activate
def test_send_batch_base64_unauthorized_upload():
    responses.add(
        responses.POST,
        f"{BASE_URL}/ocr/batch/rg",
        json={
            "urls": {"document": "https://test2.com"},
            "id": "123",
            "status_url": "https://test.com",
        },
        status=200,
    )

    responses.add(
        responses.PUT,
        "https://test2.com",
        status=401,
    )

    c = Client()
    unittest.TestCase().assertRaises(
        InvalidStatusCodeException, c.send_batch_base64, "rg", "aaa"
    )


@responses.activate
def test_wait_for_batch_done():
    responses.add(
        responses.GET,
        f"{BASE_URL}/ocr/batch/status/123",
        json={
            "batch_ksuid": "123",
            "jobs": [],
            "service": "rg",
            "status": "done",
        },
        status=200,
    )

    c = Client()
    res = c.wait_for_batch_done("123")

    assert res.get("batch_ksuid")
    assert res.get("service")
    assert res.get("status")

    assert res.get("batch_ksuid") == "123"
    assert res.get("service") == "rg"
    assert res.get("status") == "done"


@responses.activate
def test_wait_for_batch_done_with_jobs():
    responses.add(
        responses.GET,
        f"{BASE_URL}/ocr/batch/status/123",
        json={
            "batch_ksuid": "123",
            "jobs": [{"job_ksuid": "234"}],
            "service": "rg",
            "status": "done",
        },
        status=200,
    )

    responses.add(
        responses.GET,
        f"{BASE_URL}/ocr/job/result/123/234",
        json={
            "status": "done",
        },
        status=200,
    )

    c = Client()
    res = c.wait_for_batch_done("123")

    assert res.get("batch_ksuid")
    assert res.get("service")
    assert res.get("status")

    assert res.get("batch_ksuid") == "123"
    assert res.get("service") == "rg"
    assert res.get("status") == "done"


@responses.activate
def test_wait_for_batch_done_unauthorized():
    responses.add(
        responses.GET,
        f"{BASE_URL}/ocr/batch/status/123",
        status=401,
    )

    c = Client()
    unittest.TestCase().assertRaises(
        InvalidStatusCodeException, c.wait_for_batch_done, "123"
    )


@responses.activate
def test_wait_for_batch_done_timeout():
    responses.add(
        responses.GET,
        f"{BASE_URL}/ocr/batch/status/123",
        json={
            "batch_ksuid": "123",
            "service": "rg",
            "status": "processing",
        },
        status=200,
    )

    c = Client(timeout=1)
    unittest.TestCase().assertRaises(TimeoutException, c.wait_for_batch_done, "123")


@responses.activate
def test_wait_for_batch_done_timeout_job():
    responses.add(
        responses.GET,
        f"{BASE_URL}/ocr/batch/status/123",
        json={
            "batch_ksuid": "123",
            "jobs": [{"job_ksuid": "234"}],
            "service": "rg",
            "status": "done",
        },
        status=200,
    )

    responses.add(
        responses.GET,
        f"{BASE_URL}/ocr/job/result/123/234",
        json={
            "status": "processing",
        },
        status=200,
    )

    c = Client(timeout=1)
    unittest.TestCase().assertRaises(TimeoutException, c.wait_for_batch_done, "123")


@responses.activate
def test_wait_for_job_done():
    responses.add(
        responses.GET,
        f"{BASE_URL}/ocr/job/result/123/234",
        json={
            "job_ksuid": "234",
            "status": "done",
            "service": "rg",
        },
        status=200,
    )

    c = Client()
    res = c.wait_for_job_done("123", "234")

    assert res.get("job_ksuid")
    assert res.get("service")
    assert res.get("status")

    assert res.get("job_ksuid") == "234"
    assert res.get("service") == "rg"
    assert res.get("status") == "done"


@responses.activate
def test_wait_for_job_done_unauthorized():
    responses.add(
        responses.GET,
        f"{BASE_URL}/ocr/job/result/123/234",
        status=401,
    )

    c = Client()
    unittest.TestCase().assertRaises(
        InvalidStatusCodeException, c.wait_for_job_done, "123", "234"
    )


@responses.activate
def test_wait_for_job_done_timeout():
    responses.add(
        responses.GET,
        f"{BASE_URL}/ocr/job/result/123/234",
        json={
            "job_ksuid": "234",
            "service": "rg",
            "status": "processing",
        },
        status=200,
    )

    c = Client(timeout=1)
    unittest.TestCase().assertRaises(
        TimeoutException, c.wait_for_job_done, "123", "234"
    )
