import json
import os
import subprocess

import uvicorn
from fastapi import BackgroundTasks, FastAPI, Header, HTTPException, Request

app = FastAPI()

DEPLOY_SCRIPTS_FILE = os.getenv("DEPLOY_SCRIPTS_FILE", "deploy_scripts.json")

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
    if x_github_event == "push":
        payload = await request.json()
        if "ref" in payload and payload["ref"] == "refs/heads/master":
            # redeploy app given by app_name
            if app_name in DEPLOY_SCRIPTS:
                script_name = DEPLOY_SCRIPTS[app_name]
                background_tasks.add_task(deploy_application, script_name)
                return {"message": "Deployment started"}

    elif x_github_event == "ping":
        return {"message": "pong"}

    raise HTTPException(400, "Unable to process action")


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5000, log_level="info")
