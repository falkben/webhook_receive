# Webhook receive

![Python package](https://github.com/falkben/webhook_receive/workflows/Python%20package/badge.svg) [![codecov](https://codecov.io/gh/falkben/webhook_receive/branch/main/graph/badge.svg?token=O3ZG3KqxXt)](https://codecov.io/gh/falkben/webhook_receive)

Simple FastAPI application to process webhooks

## Install

```sh
python3 -m venv venv
pip install -e .
```

## Running

`uvicorn webhook_receive.main:app --port 5000` (or w/ auto reload `--reload`)

Expose server with:

`ngrok http 5000`: https://ngrok.com/

## GitHub webhook setup

payload URL (from ngrok): https://SUBDOMAIN.ngrok.io/APPNAME

just push event

## Deploy scripts

Create the `deploy_scripts.json` file

```json
{
    "APPNAME": "/usr/bin/deploy_app.sh"
}
```

*Make sure scripts have executable permissions*

Or point to a different file, with `DEPLOY_SCRIPTS_FILE` environment variable.

## Tests

`pytest`

## Todo

- secrets
- other events
