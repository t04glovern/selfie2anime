import base64
import boto3
import os
import json
import time
import io
import secrets

from PIL import Image

bucket_name = os.environ['BUCKET_NAME']
queue_name = os.environ['QUEUE_NAME']
dynamo_table = os.environ['DYNAMO_TABLE']


def selfie(event, context):
    body = json.loads(event['body'])

    email = body['email']
    try:
        email_domain = email.split('@')[1].lower()
        if email_domain == "post-shift.ru" or email_domain == "1secmail.com":
            response = {
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                },
                "statusCode": 200
            }
            return response
    except Exception as e:
        response = {
            "headers": {
                "Access-Control-Allow-Origin": "*",
            },
            "statusCode": 200
        }
        return response

    crop = body['crop']
    _, encoded = body['photo'].split(",", 1)
    image = base64.b64decode(encoded)

    cropped_image = Image.open(io.BytesIO(image))
    cropped_image = cropped_image.crop((crop['x'], crop['y'], crop['x'] + crop['width'], crop['y'] + crop['height']))
    cropped_image = cropped_image.resize((256, 256))

    cropped_image_data = io.BytesIO()
    cropped_image.save(cropped_image_data, format='jpeg', quality=95)
    cropped_image = cropped_image_data.getvalue()

    # Create S3 client and store image
    s3 = boto3.client('s3')
    folder_name = 'incoming'
    cropped_folder_name = 'incoming-cropped'
    file_name = str(secrets.token_urlsafe(30)) + '.jpg'
    file_path = folder_name + '/' + file_name
    cropped_file_path = cropped_folder_name + '/' + file_name

    s3.put_object(Body=image, Bucket=bucket_name, Key=file_path)
    s3.put_object(Body=cropped_image, Bucket=bucket_name, Key=cropped_file_path)

    # Create SQS client and send data for processing
    sqs = boto3.client('sqs')
    response = sqs.get_queue_url(QueueName=queue_name)
    queue_url = response['QueueUrl']

    # Secret delete key
    token = secrets.token_urlsafe(16)

    # Construct message
    message = {
        "bucket_name": bucket_name,
        "bucket_key": file_path,
        "bucket_cropped_key": cropped_file_path,
        "token": token,
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
            'key': file_name,
            'token': token,
            'crop': crop
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


def count(event, context):
    dynamodb = boto3.client('dynamodb')
    table = dynamodb.describe_table(
        TableName=dynamo_table
    )

    item_count = table['Table']['ItemCount']
    body = {
        "count": item_count
    }

    response = {
        "headers": {
            "Access-Control-Allow-Origin": "*",
        },
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response
