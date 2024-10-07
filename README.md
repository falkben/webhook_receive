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

or w/ auto reload: `--reload`

**Note:** in production, set up server to start automatically with gunicorn and systemd

Test locally with:

```sh
curl --fail-with-body -H "X-GitHub-Event:push" --json '{"repository": {"default_branch": "main"}, "ref": "refs/heads/main"}' -X POST http://127.0.0.1:5000/webhook/APPNAME
```

Expose local server with either (good for local testing):

- `ngrok` <https://ngrok.com/>
- `localtunnel` <https://localtunnel.github.io>

For more permanent solutions, either set up a permanent subdomain with one of the services above, or associate a domain on your own, or, if on something like a raspberrypi on a local network (without a perm. IP), create a port forwarding rule to your local server & port and use a dynamic DNS service ([FreeDNS](https://freedns.afraid.org/)).

## GitHub webhook setup

- payload URL (from ngrok or similar): <https://SUBDOMAIN.ngrok.io/APPNAME>
- Content type: `application/json`
- "just the push event"
- secrets, not currently supported, leave blank

## Deploy scripts

Default is `./deploy_scripts.json`. See example in [deploy_scripts_example.json](deploy_scripts_example.json)

_Alternatively_, you can define your deploy_scripts file in any location, and set the following environment variable to that location: `DEPLOY_SCRIPTS_FILE`.

**Note**: Ensure the associated scripts have executable permissions

```sh
chmod +x SCRIPT_NAME
```

## Docker

Create the `deploy_script.json` file and place it in the project directory. See above for how to set the config file.

To override defaults, edit the [Dockerfile](Dockerfile) or [docker-compose.yml](docker-compose.yml) and add the following environment variables and values.

| Env. Var              | Description |
| -----------           | ----------- |
| `DEPLOY_SCRIPTS_FILE` | Sets the relative path to the deploy_scripts.json file (default: `deploy_scripts.json`) |
| `GITHUB_IPS_ONLY`     | Allow requests only from GitHub IPs (default: `true`) |

Run the server ("detached" mode) with:

```sh
docker-compose up -d
```

This will run the server and set it to restart automatically with the system.

It will also bind the current directory to the docker image, so edits you make to the `deploy_script.json` will be reflected in the app, after restarting the container with `docker-compose restart`.

## Tests

`pytest`

## Todo

- [ ] secrets <https://docs.github.com/en/developers/webhooks-and-events/securing-your-webhooks#setting-your-secret-token>
- [ ] support additional webhook events

## To update requirements

Ensure you have [pip-tools](https://github.com/jazzband/pip-tools): `pip install pip-tools`

Creating the requirements.txt file (this will overwrite): `pip-compile requirements.in`

To upgrade: `pip-compile --upgrade`

## Inspiration

This project was inspired by [python-github-webhooks](https://github.com/carlos-jenkins/python-github-webhooks), which uses `flask` and supports **many** more features
