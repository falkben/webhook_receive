import os
import time
from unittest import mock

import httpx
import pytest
from fastapi.testclient import TestClient

from webhook_receive.main import app

client = TestClient(app)


@pytest.fixture()
def test_output_file():
    def remove_testfile():
        if os.path.exists("tests/data/test_out.txt"):
            os.remove("tests/data/test_out.txt")

    remove_testfile()

    yield

    remove_testfile()


@pytest.mark.asyncio
@mock.patch("webhook_receive.main.GITHUB_IPS_ONLY", True)
async def test_github_ips_only():
    # using httpx async test client here to allow setting scope (e.g. IP address)
    # httpx defaults to 127.0.0.1
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        resp = await client.post(
            "/webhook/test_app", headers={"X-GITHUB-EVENT": "ping"}
        )
    assert resp.status_code == 403
    assert resp.json() == {"detail": "Not a GitHub hooks ip address"}


def test_webhook_receive(test_output_file):
    data = {"ref": "refs/heads/master", "repository": {"default_branch": "master"}}

    resp = client.post(
        "/webhook/test_app", json=data, headers={"X-GITHUB-EVENT": "push"}
    )
    resp_data = resp.json()
    assert resp_data == {"message": "Deployment started for [test_app]"}

    # subprocess as background task... lets wait a little bit
    time.sleep(0.1)
    with open("tests/data/test_out.txt") as tf:
        test_out = tf.read().splitlines()
    assert test_out[0] == "tested"


def test_webhook_wrong_app(test_output_file):
    data = {"ref": "refs/heads/master", "repository": {"default_branch": "master"}}
    resp = client.post(
        "/webhook/NOT_AN_APP", json=data, headers={"X-GITHUB-EVENT": "push"}
    )
    assert resp.status_code == 422


def test_ping():
    resp = client.post("/webhook/test_app", headers={"X-GITHUB-EVENT": "ping"})
    assert resp.status_code == 200
    assert resp.json() == {"message": "pong"}


def test_unsupported_event():
    resp = client.post(
        "/webhook/test_app", headers={"X-GITHUB-EVENT": "unsupported_event"}
    )
    assert resp.status_code == 200
    assert resp.json() == {
        "message": "Unable to process action [unsupported_event] for [test_app]"
    }
