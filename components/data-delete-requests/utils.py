import email
import logging
import os

from email import policy

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

DYNAMODB_TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME")
if DYNAMODB_TABLE_NAME is None:
    logger.error('No DYNAMODB_TABLE_NAME value specified.')

dynamodb_client = boto3.resource('dynamodb')
dynamodb_table = dynamodb_client.Table(DYNAMODB_TABLE_NAME)

workmail_message_flow = boto3.client('workmailmessageflow')


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
    email_generation_policy = policy.SMTP.clone(refold_source='none')
    logger.info("Downloaded email from WorkMail successfully")
    return email.message_from_bytes(email_content, policy=email_generation_policy)


def remove_data_for_email(parsed_email):
    resp = dynamodb_table.query(
        # Add the name of the index you want to use in your query.
        IndexName="email-timestamp-index",
        KeyConditionExpression=Key("email").eq(parsed_email),
    )

    for item in resp['Items']:
        s3_client = boto3.resource('s3')
        # Delete outgoing
        try:
            s3_client.Object(item['bucket'], f"outgoing/{item['key']}").delete()
            logger.info("Delete successful for S3 outgoing: %s", item['key'])
        except ClientError as err:
            logger.error(
                "Failed to delete S3 outgoing: %s, error: %s", item['key'], err)
            break
        # Delete incoming-cropped
        try:
            s3_client.Object(item['bucket'], f"incoming-cropped/{item['key']}").delete()
            logger.info("Delete successful for S3 incoming-cropped: %s", item['key'])
        except ClientError as err:
            logger.error(
                "Failed to delete S3 incoming-cropped: %s, error: %s", item['key'], err)
            break
        # Delete incoming
        try:
            s3_client.Object(item['bucket'], f"incoming/{item['key']}").delete()
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
