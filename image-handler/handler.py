import base64
import boto3
import os
import json
import uuid
import time

bucket_name = os.environ['BUCKET_NAME']
queue_name = os.environ['QUEUE_NAME']
dynamo_table = os.environ['DYNAMO_TABLE']


def selfie(event, context):
    body = json.loads(event['body'])

    email = body['email']
    crop = body['crop']
    _, encoded = body['photo'].split(",", 1)
    image = base64.b64decode(encoded)

    # Create S3 client and store image
    s3 = boto3.client('s3')
    folder_name = 'incoming'
    file_name = str(uuid.uuid1())+'.jpg'
    file_path = folder_name + '/' + file_name
    response = s3.put_object(Body=image, Bucket=bucket_name, Key=file_path)

    # Create SQS client and send data for processing
    sqs = boto3.client('sqs')
    response = sqs.get_queue_url(QueueName=queue_name)
    queue_url = response['QueueUrl']

    # Construct message
    message = {
        "bucket_name": bucket_name,
        "bucket_key": file_path,
        "file_name": file_name,
        "email": email,
        "crop": crop
    }

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(dynamo_table)
    response = table.put_item(
        Item={
            'timestamp': str(time.time()),
            'email': email,
            'bucket': bucket_name,
            'key': file_name
        }
    )

    # Send message to SQS queue
    response = sqs.send_message(
        QueueUrl=queue_url, MessageBody=json.dumps(message))

    response = {
        "headers": {
            "Access-Control-Allow-Origin": "*",
        },
        "statusCode": 200
    }

    return response
