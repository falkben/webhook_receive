import ipaddress
import json
import os
import subprocess

import uvicorn
from fastapi import BackgroundTasks, FastAPI, Header, HTTPException, Request
from httpx import AsyncClient

app = FastAPI()

DEPLOY_SCRIPTS_FILE = os.getenv("DEPLOY_SCRIPTS_FILE", "deploy_scripts.json")
GITHUB_IPS_ONLY = os.getenv("GITHUB_IPS_ONLY", "True").lower() in ["true", "1"]


with open(DEPLOY_SCRIPTS_FILE) as fh:
    # load the deploy scripts from the project directory
    DEPLOY_SCRIPTS = json.load(fh)


def deploy_application(script_name):
    subprocess.run(script_name)


@app.post("/webhook/{app_name}")
async def receive_payload(
    request: Request,
    app_name: str,
    background_tasks: BackgroundTasks,
    x_github_event: str = Header(...),
):

    # Allow GitHub IPs only
    if GITHUB_IPS_ONLY:
        src_ip = ipaddress.ip_address(request.client.host)
        async with AsyncClient() as client:
            allowlist = await client.get("https://api.github.com/meta")
        for valid_ip in allowlist.json()["hooks"]:
            if src_ip in ipaddress.ip_network(valid_ip):
                break
        else:
            raise HTTPException(403, "Not a GitHub hooks ip address")

    if x_github_event == "push":
        payload = await request.json()

        default_branch = payload["repository"]["default_branch"]
        if "ref" in payload and payload["ref"] == f"refs/heads/{default_branch}":
            # redeploy app given by app_name
            if app_name in DEPLOY_SCRIPTS:
                script_name = DEPLOY_SCRIPTS[app_name]
                background_tasks.add_task(deploy_application, script_name)
                return {"message": "Deployment started"}

            return {"message": "Skipped"}

    elif x_github_event == "ping":
        return {"message": "pong"}

    else:
        return {"message": "Unable to process action"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5000, log_level="info")
