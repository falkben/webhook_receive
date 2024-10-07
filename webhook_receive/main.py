import hashlib
import hmac
import ipaddress
import json
import os
import subprocess
from enum import Enum

import uvicorn
from dotenv import load_dotenv
from fastapi import (
    BackgroundTasks,
    Depends,
    FastAPI,
    Header,
    HTTPException,
    Request,
    status,
)
from httpx import AsyncClient


def verify_signature(payload_body, secret_token, signature_header):
    """Verify that the payload was sent from GitHub by validating SHA256.

    Raise and return 403 if not authorized.

    Args:
        payload_body: original request body to verify (request.body())
        secret_token: GitHub app webhook token (WEBHOOK_SECRET)
        signature_header: header received from GitHub (x-hub-signature-256)
    """
    if not signature_header:
        raise HTTPException(
            status_code=403, detail="x-hub-signature-256 header is missing!"
        )
    hash_object = hmac.new(
        secret_token.encode("utf-8"), msg=payload_body, digestmod=hashlib.sha256
    )
    expected_signature = "sha256=" + hash_object.hexdigest()
    if not hmac.compare_digest(expected_signature, signature_header):
        raise HTTPException(status_code=403, detail="Request signatures didn't match!")


load_dotenv()

app = FastAPI()

DEPLOY_SCRIPTS_FILE = os.getenv("DEPLOY_SCRIPTS_FILE", "deploy_scripts.json")
GITHUB_IPS_ONLY = os.getenv("GITHUB_IPS_ONLY", "True").lower() in ["true", "1"]
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")


with open(DEPLOY_SCRIPTS_FILE) as fh:
    # load the deploy scripts from the project directory
    DEPLOY_SCRIPTS = json.load(fh)


def deploy_application(script_name):
    subprocess.run(script_name)


AppNames = Enum("AppNames", [(k, k) for k in DEPLOY_SCRIPTS.keys()], type=str)


async def gate_by_github_ip(request: Request):
    # Allow GitHub IPs only
    if GITHUB_IPS_ONLY:
        try:
            src_ip = ipaddress.ip_address(request.client.host)
        except ValueError:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "Could not hook sender ip address"
            )
        async with AsyncClient() as client:
            allowlist = await client.get("https://api.github.com/meta")
        for valid_ip in allowlist.json()["hooks"]:
            if src_ip in ipaddress.ip_network(valid_ip):
                return
        else:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN, "Not a GitHub hooks ip address"
            )


@app.post("/webhook/{app_name:path}", dependencies=[Depends(gate_by_github_ip)])
async def receive_payload(
    request: Request,
    app_name: AppNames,
    background_tasks: BackgroundTasks,
    x_github_event: str = Header(...),
):
    payload_body = await request.body()
    if WEBHOOK_SECRET:
        signature_header = request.headers.get("x-hub-signature-256")
        verify_signature(payload_body, WEBHOOK_SECRET, signature_header)

    if x_github_event == "push":
        payload = json.loads(payload_body)

        default_branch = payload["repository"]["default_branch"]
        # check if event is referencing the default branch
        if "ref" in payload and payload["ref"] == f"refs/heads/{default_branch}":
            # check if app_name is declared in config
            script_name = DEPLOY_SCRIPTS[app_name]
            background_tasks.add_task(deploy_application, script_name)
            return {"message": f"Deployment started for [{app_name}]"}
        else:
            return {
                "message": f"No deployment action required for [{app_name}] on ref [{payload['ref']}]"
            }

    elif x_github_event == "ping":
        return {"message": "pong"}

    else:
        return {
            "message": f"Unable to process action [{x_github_event}] for [{app_name}]"
        }


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5000, log_level="info")
