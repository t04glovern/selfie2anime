import base64
import boto3
import os
import time
import json

bucket_name = os.environ['BUCKET_NAME']
queue_name = os.environ['QUEUE_NAME']


def selfie(event, context):
    body = json.loads(event['body'])

    email = body['email']
    crop = body['crop']
    _, encoded = body['photo'].split(",", 1)
    image = base64.b64decode(encoded)

    # Create S3 client and store image
    s3 = boto3.client('s3')
    file_name = 'archive/image-'+time.strftime("%Y%m%d-%H%M%S")+'.jpg'
    response = s3.put_object(Body=image, Bucket=bucket_name, Key=file_name)

    # Create SQS client and send data for processing
    sqs = boto3.client('sqs')
    response = sqs.get_queue_url(QueueName=queue_name)
    queue_url = response['QueueUrl']

    # Construct message
    message = {
        "bucket_name": bucket_name,
        "bucket_key": file_name,
        "email": email,
        "crop": crop
    }

    # Send message to SQS queue
    response = sqs.send_message(QueueUrl=queue_url, MessageBody=json.dumps(message))

    response = {
        "headers": {
            "Access-Control-Allow-Origin": "*",
        },
        "statusCode": 200
    }

    return response
