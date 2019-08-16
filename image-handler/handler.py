import base64
import boto3
import os
import time

bucket_name = os.environ['BUCKET_NAME']
queue_name = os.environ['QUEUE_NAME']


def selfie(event, context):
    body = event['body']
    email = body['email']
    image = base64.b64decode(body['image'])

    # Create S3 client and store image
    s3 = boto3.client('s3')
    file_name = 'archive/image-'+time.strftime("%Y%m%d-%H%M%S")+'.jpg'
    response = s3.put_object(Body=image, Bucket=bucket_name, Key=file_name)

    # Create SQS client and send data for processing
    sqs = boto3.client('sqs')
    response = sqs.get_queue_url(QueueName=queue_name)
    queue_url = response['QueueUrl']

    # Send message to SQS queue
    response = sqs.send_message(QueueUrl=queue_url, MessageBody=body['image'], MessageAttributes={
        'Email': {
            'StringValue': email,
            'DataType': 'String'
        }
    })

    response = {
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": "true",
        },
        "statusCode": 200,
        "body": {
            "image": "https://s3.amazonaws.com/" + bucket_name + "/" + file_name,
            "message_md5": response['MD5OfMessageBody'],
            "email": email
        }
    }

    return response
