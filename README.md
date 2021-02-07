# Webhook receive

![Python package](https://github.com/falkben/webhook_receive/workflows/Python%20package/badge.svg) [![codecov](https://codecov.io/gh/falkben/webhook_receive/branch/main/graph/badge.svg?token=O3ZG3KqxXt)](https://codecov.io/gh/falkben/webhook_receive)

Simple FastAPI application to process webhooks

## WIP

This is a work in progress and should be used with caution.

## Features

- Run `bash` or other scripts in response to GitHub webhook events (currently only support events on the default branch)
- Scripts registered to specific apps through a config file
- By defining the association of scripts and events in a config file, a single instance of this server can respond to webhook events across different projects, running different scripts for each project

## Install

```sh
git clone https://github.com/falkben/webhook_receive.git
cd webhook_receive
python3 -m venv venv
. venv/bin/activate
pip install -e .
```

## Running

```sh
uvicorn webhook_receive.main:app --port 5000
```

(or w/ auto reload `--reload`)

**Note:** in production, set up server to start automatically with gunicorn and systemd

Expose server with:

`ngrok http 5000`: <https://ngrok.com/>

## GitHub webhook setup

- payload URL (from ngrok): https://SUBDOMAIN.ngrok.io/APPNAME
- just push event
- (secrets not currently supported, leave blank)

## Deploy scripts

Default is `./deploy_scripts.json`. See example in [deploy_scripts_example.json](deploy_scripts_example.json)

_Alternatively_, you can define your deploy_scripts file in any location, and set the following environment variable to that location: `DEPLOY_SCRIPTS_FILE`.

**Note**: Ensure the associated scripts have executable permissions

```sh
chmod +x SCRIPT_NAME
```

## Docker

First, create the `deploy_script.json` file and place it in the project directory. See above for how to set the config file.

The app, by default, sets the deploy scripts location to the project directory, and limits incoming requests to github webhook ips. To change these, edit the [Dockerfile](Dockerfile) and add:

- `ENV DEPLOY_SCRIPTS_FILE=script_location.json`
- `ENV GITHUB_IPS_ONLY=false`

Finally, run the server ("detached" mode) with:

```sh
docker-compose up -d
```

## Tests

`pytest`

## Todo

- [ ] secrets <https://docs.github.com/en/developers/webhooks-and-events/securing-your-webhooks#setting-your-secret-token>
- [ ] other webhook events

## Inspiration

This project was inspired by [python-github-webhooks](https://github.com/carlos-jenkins/python-github-webhooks), which uses `flask` and supports many more features
