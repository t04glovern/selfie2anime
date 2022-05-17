# Data Delete Requests

## Setup Serverless

```bash
npm install -g serverless
serverless config credentials --provider aws --key <ACCESS KEY ID> --secret <SECRET KEY>
```

## WorkMail Setup

Create a `config.json` file containing the WorkMail Organisation ID

```json
{
    "org_id": "m-xxxxxxxxxxxxxxxxxxxxxxxxxxxx"
}
```

## Deploy

```bash
serverless deploy
```

## Invoke Function

You can invoke your deployed functions using the following

```bash
# Activate a python envirionment locally
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip boto3
```
