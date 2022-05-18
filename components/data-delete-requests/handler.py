import logging
import utils
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def mail(event, context):
    """
    Translate Email Content Using WorkMail Lambda Integration
    Parameters
    ----------
    email_summary: dict, required
        Amazon WorkMail Message Summary Input Format
        For more information, see https://docs.aws.amazon.com/workmail/latest/adminguide/lambda.html
        {
            "summaryVersion": "2019-07-28",                         # AWS WorkMail Message Summary Version
            "envelope": {
                "mailFrom" : {
                    "address" : "from@domain.test"                  # String containing from email address
                },
                "recipients" : [                                    # List of all recipient email addresses
                   { "address" : "recipient1@domain.test" },
                   { "address" : "recipient2@domain.test" }
                ]
            },
            "sender" : {
                "address" :  "sender@domain.test"                   # String containing sender email address
            },
            "subject" : "Hello From Amazon WorkMail!",              # String containing email subject (Truncated to first 256 chars)"
            "messageId": "00000000-0000-0000-0000-000000000000",    # String containing message id for retrieval using workmail flow API
            "invocationId": "00000000000000000000000000000000",     # String containing the id of this lambda invocation. Useful for detecting retries and avoiding duplication
            "flowDirection": "INBOUND",                             # String indicating direction of email flow. Value is either "INBOUND" or "OUTBOUND"
            "truncated": false                                      # boolean indicating if any field in message was truncated due to size limitations
        }
    context: object, required
    Lambda Context runtime methods and attributes. See https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html
    Returns
    -------
    Amazon WorkMail Sync Lambda Response Format
    For more information, see https://docs.aws.amazon.com/workmail/latest/adminguide/lambda.html#synchronous-schema
        return {
          'actions': [                                              # Required, should contain at least 1 list element
          {
            'action' : {                                            # Required
              'type': 'string',                                     # Required. Can be "BOUNCE", "DROP" or "DEFAULT"
              'parameters': { <various> }                           # Optional. For bounce, <various> can be {"bounceMessage": "message that goes in bounce mail"}
            },
            'recipients': list of strings,                          # Optional. Indicates list of recipients for which this action applies
            'default': boolean                                      # Optional. Indicates whether this action applies to all recipients
          }
        ]}
    """

    logger.info("Received event: %s", event)
    message_id = event['messageId']
    from_addr = event['envelope']['mailFrom']['address']
    subject = event['subject']
    try:
        downloaded_email = utils.download_email(message_id)
        text_body = utils.extract_text_body(downloaded_email)

        if subject.startswith('Selfie2anime data erasure request'):
            logger.info("Received data erasure request from %s", from_addr)
            logger.info("Email subject: %s", subject)
            logger.info("Email text body: %s", text_body)
            utils.remove_data_for_email(parsed_email=from_addr)
            updated_email = utils.update_email_subject(downloaded_email=downloaded_email, email_subject=subject)
            utils.update_workmail_email(message_id=message_id, content=updated_email)
            utils.send_confirmation_email(parsed_email=from_addr)
        else:
            logger.info(
                "Email with subject: %s is not a data erasure request", subject)
    except ClientError as error:
        if error.response['Error']['Code'] == 'MessageFrozen':
            # Redirect emails are not eligible for update, handle it gracefully.
            logger.info(
                "Message %s is not eligible for update. This is usually the case for a redirected email", message_id)
        else:
            logger.error(error.response['Error']['Message'])
            if error.response['Error']['Code'] == 'ResourceNotFoundException':
                logger.error(
                    "Message %s does not exist. Messages in transit are no longer accessible after 1 day", message_id)
            elif error.response['Error']['Code'] == 'InvalidContentLocation':
                logger.error(
                    'WorkMail could not access the updated email content. See https://docs.aws.amazon.com/workmail/latest/adminguide/update-with-lambda.html')
            raise(error)

    return {
        'actions': [{
            'action': {
                'type': 'DEFAULT'
            },
            'allRecipients': 'true'
        }]
    }
