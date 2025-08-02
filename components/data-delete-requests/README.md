# Data Delete Requests

## Setup Serverless

```bash
npm install -g serverless@2.72.4
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

## Export Data

Comment back in the Resources relating to Email export, deploy and then run the following to export emails from WorkMail

You will also need to update the config.json file to have a field for `kms_admin_role`.

```bash
aws workmail start-mailbox-export-job \
    --organization-id $WORKMAIL_ORG_ID \
    --entity-id $WORKMAIL_USER_ID \
    --kms-key-arn $WorkMailExportBucketKey_arn \
    --role-arn $WorkMailExportRole_arn \
    --s3-bucket-name $WorkMailExportBucket_name \
    --s3-prefix export

aws workmail list-mailbox-export-jobs \
    --organization-id $WORKMAIL_ORG_ID

aws workmail describe-mailbox-export-job \
    --organization-id $WORKMAIL_ORG_ID \
    --job-id $JOB_ID_FROM_ABOVE
```
