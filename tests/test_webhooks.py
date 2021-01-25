import os
import time

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


def test_webhook_receive(test_output_file):

    data = {"ref": "refs/heads/master", "repository": {"default_branch": "master"}}

    resp = client.post(
        "/webhook/test_app", json=data, headers={"X-GITHUB-EVENT": "push"}
    )
    resp_data = resp.json()
    assert resp_data == {"message": "Deployment started"}

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
    assert resp.status_code == 200
    assert resp.json() == {"message": "Skipped"}


def test_ping():
    resp = client.post("/webhook/doesnt_matter", headers={"X-GITHUB-EVENT": "ping"})
    assert resp.status_code == 200
    assert resp.json() == {"message": "pong"}
