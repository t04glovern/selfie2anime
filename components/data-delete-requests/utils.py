import email
import logging
import os
import uuid

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

DYNAMODB_TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME")
if DYNAMODB_TABLE_NAME is None:
    logger.info('No DYNAMODB_TABLE_NAME value specified. Defaulting to selfie2anime')
    DYNAMODB_TABLE_NAME = "selfie2anime"

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
if SENDER_EMAIL is None:
    logger.info('No SENDER_EMAIL value specified. Defaulting to legal@selfie2anime.com')
    SENDER_EMAIL = "legal@selfie2anime.com"

dynamodb_client = boto3.resource('dynamodb')
dynamodb_table = dynamodb_client.Table(DYNAMODB_TABLE_NAME)

workmail_message_flow = boto3.client('workmailmessageflow')
ses_client = boto3.client('ses')

UPDATED_EMAIL_BUCKET = os.getenv('UPDATED_EMAIL_BUCKET')
if not UPDATED_EMAIL_BUCKET:
    logger.info('No UPDATED_EMAIL_BUCKET value specified. Defaulting to selfie2anime-data-emails')
    UPDATED_EMAIL_BUCKET = "selfie2anime-data-emails"

s3_client = boto3.client('s3')
s3_resource = boto3.resource('s3')

def extract_text_body(parsed_email):
    """
    Extract email message content of type "text/plain" from a parsed email
    Parameters
    ----------
    parsed_email: email.message.Message, required
        The parsed email as returned by download_email
    Returns
    -------
    string
        string containing text/plain email body decoded with according to the
        Content-Transfer-Encoding header and then according to content charset.
    None
        No content of type "text/plain" is found.
    """
    text_content = None
    text_charset = None
    if parsed_email.is_multipart():
        # Walk over message parts of this multipart email.
        for part in parsed_email.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get_content_disposition())
            if content_type == 'text/plain' and 'attachment' not in content_disposition:
                text_content = part.get_payload(decode=True)
                text_charset = part.get_content_charset()
                break
    else:
        text_content = parsed_email.get_payload(decode=True)
        text_charset = parsed_email.get_content_charset()

    if text_content and text_charset:
        return text_content.decode(text_charset)
    return


def download_email(message_id):
    """
    This method downloads full email MIME content using GetRawMessageContent API and
    uses email.parser class for parsing it into Python email.message.EmailMessage class.
    Reference:
        https://docs.python.org/3.7/library/email.message.html#email.message.EmailMessage
        https://docs.python.org/3/library/email.parser.html
    Parameters
    ----------
    message_id: string, required
        message_id of the email to download
    Returns
    -------
    email.message.Message
        EmailMessage representation the downloaded email
    """
    response = workmail_message_flow.get_raw_message_content(
        messageId=message_id)
    email_content = response['messageContent'].read()
    logger.info("Downloaded email from WorkMail successfully")
    return email.message_from_bytes(email_content)


def update_email_subject(downloaded_email, email_subject):
    """
    Updates the subject of the downloaded email.
    Parameters
    ----------
    downloaded_email: email.message.Message, required
         EmailMessage representation the original downloaded email
    email_subject: string, required
        Subject of the email
    Returns
    -------
    email.message.Message
        EmailMessage representation the updated email.
    """
    new_subject =  f"[ACTIONED] {email_subject}"
    downloaded_email.replace_header('Subject', new_subject)
    logger.info("Message subject modified to: %s", new_subject)
    return downloaded_email


def update_workmail_email(message_id, content):
    """
    Uploads the updated message to an S3 bucket in your account and then updates it at WorkMail via
    PutRawMessageContent API.
    Reference: https://docs.aws.amazon.com/workmail/latest/adminguide/update-with-lambda.html
    Parameters
    ----------
    message_id: string, required
        message_id of the email to download
    content: email.message.Message, required
         EmailMessage representation the updated email
    Returns
    -------
    None
    """

    key = str(uuid.uuid4())
    s3_client.put_object(Body=content.as_bytes(), Bucket=UPDATED_EMAIL_BUCKET, Key=key)
    s3_reference = {
        'bucket': UPDATED_EMAIL_BUCKET,
        'key': key
    }
    content = {
        's3Reference': s3_reference
    }
    workmail_message_flow.put_raw_message_content(messageId=message_id, content=content)
    logger.info("Updated email with msg_id: %s sent to WorkMail successfully", message_id)


def remove_data_for_email(parsed_email):
    """
    Removes data for a given email address
    Parameters
    ----------
    parsed_email: string, required
        The parsed email address to delete data for
    Returns
    -------
    None
    """
    resp = dynamodb_table.query(
        # Add the name of the index you want to use in your query.
        IndexName="email-timestamp-index",
        KeyConditionExpression=Key("email").eq(parsed_email),
    )

    for item in resp['Items']:
        # Delete outgoing
        try:
            s3_resource.Object(item['bucket'], f"outgoing/{item['key']}").delete()
            logger.info("Delete successful for S3 outgoing: %s", item['key'])
        except ClientError as err:
            logger.error(
                "Failed to delete S3 outgoing: %s, error: %s", item['key'], err)
            break
        # Delete incoming-cropped
        try:
            s3_resource.Object(item['bucket'], f"incoming-cropped/{item['key']}").delete()
            logger.info("Delete successful for S3 incoming-cropped: %s", item['key'])
        except ClientError as err:
            logger.error(
                "Failed to delete S3 incoming-cropped: %s, error: %s", item['key'], err)
            break
        # Delete incoming
        try:
            s3_resource.Object(item['bucket'], f"incoming/{item['key']}").delete()
            logger.info("Delete successful for S3 incoming: %s", item['key'])
        except ClientError as err:
            logger.error(
                "Failed to delete S3 incoming: %s, error: %s", item['key'], err)
            break
        # Delete DynamoDB record
        try:
            dynamodb_table.delete_item(
                TableName=DYNAMODB_TABLE_NAME,
                Key={
                    "timestamp": item['timestamp'],
                    "email": item['email']
                }
            )
            logger.info("Delete successful for DynamoDB item email: %s @ %s", item['timestamp'], item['email'])
        except ClientError as err:
            logger.error("Failed to delete DynamoDB item email: %s @ %s, error: %s", item['timestamp'], item['email'], err)
            break


def send_confirmation_email(parsed_email):
    """
    Sends confirmation email to email of customer requesting data deletion
    Parameters
    ----------
    parsed_email: string, required
        The parsed email address to delete data for
    Returns
    -------
    None
    """
    charset = "UTF-8"
    html_email_content = """
        <html>
            <head></head>
            <p>Hi,</p>
            <p>This is a confirmation that all your data associated with this email has been removed.</p><br>
            <p>Regards,</p>
            <p>Selfie2Anime Team</p>
            </body>
        </html>
    """

    try:
        ses_client.send_email(
            Destination={
                "ToAddresses": [
                    parsed_email,
                ],
            },
            Message={
                "Body": {
                    "Html": {
                        "Charset": charset,
                        "Data": html_email_content,
                    }
                },
                "Subject": {
                    "Charset": charset,
                    "Data": "Selfie2anime data erasure request - Confirmation",
                },
            },
            Source=SENDER_EMAIL,
        )
        logger.info("Confirmation email sent to: %s", parsed_email)
    except ClientError as err:
        logger.error("Failed to send confirmation email to: %s, error: %s", parsed_email, err)
    