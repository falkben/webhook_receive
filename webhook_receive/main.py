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

load_dotenv()

app = FastAPI()

DEPLOY_SCRIPTS_FILE = os.getenv("DEPLOY_SCRIPTS_FILE", "deploy_scripts.json")
GITHUB_IPS_ONLY = os.getenv("GITHUB_IPS_ONLY", "True").lower() in ["true", "1"]


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

    if x_github_event == "push":
        payload = await request.json()

        default_branch = payload["repository"]["default_branch"]
        # check if event is referencing the default branch
        if "ref" in payload and payload["ref"] == f"refs/heads/{default_branch}":
            # check if app_name is declared in config
            script_name = DEPLOY_SCRIPTS[app_name]
            background_tasks.add_task(deploy_application, script_name)
            return {"message": f"Deployment started for [{app_name}]"}
        else:
            return {"message": f"No deployment action required for [{app_name}] on ref [{payload['ref']}]"}

    elif x_github_event == "ping":
        return {"message": "pong"}

    else:
        return {"message": f"Unable to process action [{x_github_event}] for [{app_name}]"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5000, log_level="info")
