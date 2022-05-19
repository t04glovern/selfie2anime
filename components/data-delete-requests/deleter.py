import logging
from email import message_from_file
import glob

import utils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

PATH_TO_MESSAGES = "./emails/"
DRYRUN = True

if __name__ == '__main__':
    eml_files = glob.glob(PATH_TO_MESSAGES + '*.eml')

    for eml_file in eml_files:
        msg = message_from_file(open(eml_file))

        from_addr = msg['from']
        subject = msg['subject']

        if msg['subject'].startswith('Selfie2anime data erasure request'):
            logger.info("Received data erasure request from %s", from_addr)
            logger.info("Email subject: %s", subject)
            if not DRYRUN:
                utils.remove_data_for_email(parsed_email=from_addr)
                utils.send_confirmation_email(parsed_email=from_addr)
