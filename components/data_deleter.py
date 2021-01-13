import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

bucket_name = 'selfie2anime'
dynamo_table = 'selfie2anime'
emails = [
    'fake@fake.com'
]

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(dynamo_table)

for email in emails:

    resp = table.query(
        # Add the name of the index you want to use in your query.
        IndexName="email-timestamp-index",
        KeyConditionExpression=Key('email').eq(email),
    )

    for item in resp['Items']:
        s3 = boto3.resource('s3')
        # Delete outgoing
        try:
            s3.Object(item['bucket'], 'outgoing/{}'.format(item['key'])).delete()
        except Exception as e:
            print('Failed to delete S3 outgoing: {}'.format(item['key']))
            break
        # Delete incoming-cropped
        try:
            s3.Object(item['bucket'], 'incoming-cropped/{}'.format(item['key'])).delete()
        except Exception as e:
            print('Failed to delete S3 incoming-cropped: {}'.format(item['key']))
            break
        # Delete incoming
        try:
            s3.Object(item['bucket'], 'incoming/{}'.format(item['key'])).delete()
        except Exception as e:
            print('Failed to delete S3 incoming: {}'.format(item['key']))
            break
        # Delete DynamoDB record
        try:
            response = table.delete_item(
                TableName=dynamo_table,
                Key={
                    "timestamp": item['timestamp'],
                    "email": item['email']
                }
            )
        except ClientError as err:
            print('Failed to delete DynamoDB item email: {} @ {}'.format(item['timestamp'], item['email']))
            break
