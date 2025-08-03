# Image Handler

## Setup Serverless

```bash
npm install -g serverless@^4.17.2
# Note: Serverless Framework v4 requires authentication
serverless login
```

## Python & Domain Requirements

```bash
serverless plugin install -n serverless-python-requirements
serverless plugin install -n serverless-domain-manager
```

Add the following to the `serverless.yml` file

```yaml
plugins:
  - serverless-python-requirements
  - serverless-domain-manager

custom:
  pythonRequirements:
    dockerizePip: true
```

## Deploy

```bash
npm install
serverless create_domain # can take up to 40 minutes
serverless deploy
```

## Invoke Function

You can invoke your deployed functions using the following

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Test locally
serverless invoke local -f selfie --path test_data.json
serverless invoke local -f count

# Test Deployed version
serverless invoke -f selfie --path test_data.json
```

## Attribution

* [How to set up a custom domain name for Lambda & API Gateway with Serverless](https://serverless.com/blog/serverless-api-gateway-domain/)
* [Custom domain in AWS API Gateway](https://medium.com/@maciejtreder/custom-domain-in-aws-api-gateway-a2b7feaf9c74)
* [maciejtreder/serverless-apigw-binary](https://github.com/maciejtreder/serverless-apigw-binary)
