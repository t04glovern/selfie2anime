import boto3
import os
from string import Template
from time import time

from boto3.dynamodb.conditions import Key

dynamo_table = os.environ['DYNAMO_TABLE']
cloudfront_dist = os.environ['CLOUDFRONT_DIST']


def delete(event, context):
    uuid = event['queryStringParameters']['uuid']
    key = event['queryStringParameters']['key']

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(dynamo_table)

    resp = table.query(
        # Add the name of the index you want to use in your query.
        IndexName="key-index",
        KeyConditionExpression=Key('key').eq(uuid),
    )

    for item in resp['Items']:
        if item['token'] == key:

            s3 = boto3.resource('s3')
            # Delete outgoing
            try:
                s3.Object(item['bucket'], 'outgoing/{}'.format(item['key'])).delete()
            except Exception as e:
                print('Failed to delete S3 outgoing: {}'.format(item['key']))
            # Delete incoming-cropped
            try:
                s3.Object(item['bucket'], 'incoming-cropped/{}'.format(item['key'])).delete()
            except Exception as e:
                print('Failed to delete S3 incoming-cropped: {}'.format(item['key']))
            # Delete incoming
            try:
                s3.Object(item['bucket'], 'incoming/{}'.format(item['key'])).delete()
            except Exception as e:
                print('Failed to delete S3 incoming: {}'.format(item['key']))

            try:
                client = boto3.client('cloudfront')
                response = client.create_invalidation(
                    DistributionId=cloudfront_dist,
                    InvalidationBatch={
                    'Paths': {
                        'Quantity': 1,
                        'Items': [
                            '/outgoing/{}'.format(item['key'])
                            ],
                        },
                    'CallerReference': str(time()).replace(".", "")
                    }
                )
            except Exception as e:
                print('Failed to invalidate cache for: {}'.format(item['key']))

            html_body = """
            <!DOCTYPE html>
            <html lang="en" xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml"
                xmlns:o="urn:schemas-microsoft-com:office:office">

            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width">
                <meta http-equiv="X-UA-Compatible" content="IE=edge">
                <meta http-equiv="refresh" content="7; url=https://selfie2anime.com/">
                <title>Selfie Deleted | Selfie2Anime</title>
                <link href="https://fonts.googleapis.com/css?family=Merriweather+Sans:400,400i,700,700i" rel="stylesheet">
                <style>
                    * {
                        -ms-text-size-adjust: 100%;
                        -webkit-text-size-adjust: 100%;
                    }

                    html,
                    body {
                        margin: 0 auto !important;
                        padding: 0 !important;
                        height: 100% !important;
                        width: 100% !important;
                        background: #f1f1f1;
                    }

                    div[style*="margin: 16px 0"] {
                        margin: 0 !important;
                    }

                    table,
                    td {
                        mso-table-lspace: 0pt !important;
                        mso-table-rspace: 0pt !important;
                    }

                    table {
                        border-spacing: 0 !important;
                        border-collapse: collapse !important;
                        table-layout: fixed !important;
                        margin: 0 auto !important;
                    }

                    img {
                        -ms-interpolation-mode: bicubic;
                    }

                    a {
                        text-decoration: none;
                    }

                    *[x-apple-data-detectors],
                    .unstyle-auto-detected-links *,
                    .aBn {
                        border-bottom: 0 !important;
                        cursor: default !important;
                        color: inherit !important;
                        text-decoration: none !important;
                        font-size: inherit !important;
                        font-family: inherit !important;
                        font-weight: inherit !important;
                        line-height: inherit !important;
                    }

                    .a6S {
                        display: none !important;
                        opacity: 0.01 !important;
                    }

                    .im {
                        color: inherit !important;
                    }

                    img.g-img+div {
                        display: none !important;
                    }

                    @media only screen and (min-device-width: 320px) and (max-device-width: 374px) {
                        u~div .email-container {
                            min-width: 320px !important;
                        }
                    }

                    @media only screen and (min-device-width: 375px) and (max-device-width: 413px) {
                        u~div .email-container {
                            min-width: 375px !important;
                        }
                    }

                    @media only screen and (min-device-width: 414px) {
                        u~div .email-container {
                            min-width: 414px !important;
                        }
                    }
                </style>
                <style>
                    .bg_primary {
                        background: #f06292;
                    }

                    .text_primary {
                        color: #f06292;
                        font-weight: bold;
                    }

                    .try_again {
                        font-size: 2em;
                    }

                    .bg_white {
                        background: #fff;
                    }

                    .bg_dark {
                        background: rgba(0, 0, 0, .8);
                    }

                    .email-section {
                        padding: 2.5em;
                    }

                    h1,
                    h2,
                    h3,
                    h4,
                    h5,
                    h6 {
                        font-family: 'Merriweather Sans', sans-serif;
                        color: #000;
                        margin-top: 0;
                    }

                    body {
                        font-family: 'Merriweather Sans', sans-serif;
                        font-weight: 400;
                        font-size: 18px;
                        line-height: 1.8;
                        color: rgba(0, 0, 0, .7);
                    }

                    a {
                        color: #f06292;
                        font-weight: bold;
                    }

                    .logo h1 {
                        margin: 0;
                    }

                    .logo h1 a {
                        color: #000;
                        font-size: 24px;
                        font-weight: 700;
                        text-transform: uppercase;
                        font-family: 'Merriweather Sans', sans-serif;
                    }

                    .navigation {
                        padding: 0;
                    }

                    .navigation li {
                        list-style: none;
                        display: inline-block;
                        ;
                        margin-left: 5px;
                        font-size: 12px;
                        font-weight: 700;
                        text-transform: uppercase;
                    }

                    .navigation li a {
                        color: rgba(0, 0, 0, .6);
                    }

                    .heading-section h2 {
                        color: #000;
                        font-size: 28px;
                        margin-top: 0;
                        line-height: 1.4;
                        font-weight: 700;
                    }

                    .heading-section .subheading {
                        margin-bottom: 20px !important;
                        display: inline-block;
                        font-size: 13px;
                        text-transform: uppercase;
                        letter-spacing: 2px;
                        color: rgba(0, 0, 0, .4);
                        position: relative;
                    }

                    .heading-section .subheading::after {
                        position: absolute;
                        left: 0;
                        right: 0;
                        bottom: -10px;
                        content: '';
                        width: 100%;
                        height: 2px;
                        background: #f5564e;
                        margin: 0 auto;
                    }

                    .heading-section-white {
                        color: rgba(255, 255, 255, .8);
                    }

                    .heading-section-white h2 {
                        line-height: 1;
                        padding-bottom: 0;
                    }

                    .heading-section-white h2 {
                        color: #fff;
                    }

                    .heading-section-white .subheading {
                        margin-bottom: 0;
                        display: inline-block;
                        font-size: 13px;
                        text-transform: uppercase;
                        letter-spacing: 2px;
                        color: rgba(255, 255, 255, .4);
                    }

                    .call-to-action {
                        padding: 1em 2em;
                        background: #f06292;
                        color: #fff;
                        border-radius: 999px;
                    }
                </style>
            </head>

            <body width="100%" style="margin: 0; padding: 0 !important; mso-line-height-rule: exactly; background-color: #222;">
                <center style="width: 100%; background-color: #f1f1f1;">
                    <div
                        style="display: none; font-size: 1px;max-height: 0px; max-width: 0px; opacity: 0; overflow: hidden; mso-hide: all; font-family: sans-serif;">
                        &zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;
                    </div>
                    <div style="max-width: 600px; margin: 0 auto;" class="email-container">
                        <table align="center" role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%"
                            style="margin: auto;">
                            <tr>
                                <td valign="top" class="bg_white" style="padding: 1em 2.5em;">
                                    <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%">
                                        <tr>
                                            <td width="60%" class="logo" style="text-align: left;">
                                                <h1>
                                                    <a href="https://selfie2anime.com">
                                                        Selfie<span class="text_primary">2</span>Anime&nbsp;<span
                                                            class="text_primary">アニメ</span>
                                                    </a>
                                                </h1>
                                            </td>
                                            <td width="40%" class="logo" style="text-align: right;">
                                                <a href="https://www.facebook.com/sharer/sharer.php?u=https://selfie2anime.com">
                                                    <img width="32" height="32" src="https://selfie2anime.com/email/facebook.png"
                                                        alt="Share on Facebook">
                                                </a>
                                                <a href="https://twitter.com/intent/tweet?url=https://selfie2anime.com&text=What do YOU look like in anime?&hashtags=selfie2anime"
                                                    target="_blank">
                                                    <img width="32" height="32" src="https://selfie2anime.com/email/twitter.png"
                                                        alt="Share on Twitter">
                                                </a>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                            <tr>
                                <td valign="middle" class="bg_white" style="padding: 80px 0;">
                                    <div class="overlay"></div>
                                    <table>
                                        <tr>
                                            <td>
                                                <div class="text" style="text-align: center; margin: 0 20px">
                                                    Your anime-selfie has been <b>permanently deleted</b>.
                                                </div>

                                                <div class="text" style="text-align: center; margin: 4em 0">
                                                    <a href="https://selfie2anime.com/" class="call-to-action">
                                                        GENERATE ANOTHER ONE!
                                                    </a>
                                                </div>

                                                <div class="text" style="text-align: center; font-size: 8pt; margin: 0 20px">
                                                    You will be automatically redirected to <a
                                                        href="https://selfie2anime.com/">selfie2anime.com</a>.
                                                </div>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                            <tr>
                                <td valign="middle" class="bg_primary"
                                    style="background-image: url(https://selfie2anime.com/email/wall.jpg); background-size: cover; height: 480px;">
                                </td>
                            </tr>
                            <tr>
                                <td class="bg_dark email-section" style="text-align:center;">
                                    <div class="heading-section heading-section-white">
                                        <p>
                                            Copyright &copy; 2019-2020 by
                                            <a href="https://selfie2anime.com">Selfie2Anime.com</a>
                                        </p>
                                    </div>
                                </td>
                            </tr>
                        </table>
                    </div>
                </center>
            </body>
            </html>
            """
        else:
            html_body = """
            <!DOCTYPE html>
            <html lang="en" xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml"
                xmlns:o="urn:schemas-microsoft-com:office:office">

            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width">
                <meta http-equiv="X-UA-Compatible" content="IE=edge">
                <title>Selfie Error | Selfie2Anime</title>
                <link href="https://fonts.googleapis.com/css?family=Merriweather+Sans:400,400i,700,700i" rel="stylesheet">
                <style>
                    * {
                        -ms-text-size-adjust: 100%;
                        -webkit-text-size-adjust: 100%;
                    }

                    html,
                    body {
                        margin: 0 auto !important;
                        padding: 0 !important;
                        height: 100% !important;
                        width: 100% !important;
                        background: #f1f1f1;
                    }

                    div[style*="margin: 16px 0"] {
                        margin: 0 !important;
                    }

                    table,
                    td {
                        mso-table-lspace: 0pt !important;
                        mso-table-rspace: 0pt !important;
                    }

                    table {
                        border-spacing: 0 !important;
                        border-collapse: collapse !important;
                        table-layout: fixed !important;
                        margin: 0 auto !important;
                    }

                    img {
                        -ms-interpolation-mode: bicubic;
                    }

                    a {
                        text-decoration: none;
                    }

                    *[x-apple-data-detectors],
                    .unstyle-auto-detected-links *,
                    .aBn {
                        border-bottom: 0 !important;
                        cursor: default !important;
                        color: inherit !important;
                        text-decoration: none !important;
                        font-size: inherit !important;
                        font-family: inherit !important;
                        font-weight: inherit !important;
                        line-height: inherit !important;
                    }

                    .a6S {
                        display: none !important;
                        opacity: 0.01 !important;
                    }

                    .im {
                        color: inherit !important;
                    }

                    img.g-img+div {
                        display: none !important;
                    }

                    @media only screen and (min-device-width: 320px) and (max-device-width: 374px) {
                        u~div .email-container {
                            min-width: 320px !important;
                        }
                    }

                    @media only screen and (min-device-width: 375px) and (max-device-width: 413px) {
                        u~div .email-container {
                            min-width: 375px !important;
                        }
                    }

                    @media only screen and (min-device-width: 414px) {
                        u~div .email-container {
                            min-width: 414px !important;
                        }
                    }
                </style>
                <style>
                    .bg_primary {
                        background: #f06292;
                    }

                    .text_primary {
                        color: #f06292;
                        font-weight: bold;
                    }

                    .try_again {
                        font-size: 2em;
                    }

                    .bg_white {
                        background: #fff;
                    }

                    .bg_dark {
                        background: rgba(0, 0, 0, .8);
                    }

                    .email-section {
                        padding: 2.5em;
                    }

                    h1,
                    h2,
                    h3,
                    h4,
                    h5,
                    h6 {
                        font-family: 'Merriweather Sans', sans-serif;
                        color: #000;
                        margin-top: 0;
                    }

                    body {
                        font-family: 'Merriweather Sans', sans-serif;
                        font-weight: 400;
                        font-size: 18px;
                        line-height: 1.8;
                        color: rgba(0, 0, 0, .7);
                    }

                    a {
                        color: #f06292;
                        font-weight: bold;
                    }

                    .logo h1 {
                        margin: 0;
                    }

                    .logo h1 a {
                        color: #000;
                        font-size: 24px;
                        font-weight: 700;
                        text-transform: uppercase;
                        font-family: 'Merriweather Sans', sans-serif;
                    }

                    .navigation {
                        padding: 0;
                    }

                    .navigation li {
                        list-style: none;
                        display: inline-block;
                        ;
                        margin-left: 5px;
                        font-size: 12px;
                        font-weight: 700;
                        text-transform: uppercase;
                    }

                    .navigation li a {
                        color: rgba(0, 0, 0, .6);
                    }

                    .heading-section h2 {
                        color: #000;
                        font-size: 28px;
                        margin-top: 0;
                        line-height: 1.4;
                        font-weight: 700;
                    }

                    .heading-section .subheading {
                        margin-bottom: 20px !important;
                        display: inline-block;
                        font-size: 13px;
                        text-transform: uppercase;
                        letter-spacing: 2px;
                        color: rgba(0, 0, 0, .4);
                        position: relative;
                    }

                    .heading-section .subheading::after {
                        position: absolute;
                        left: 0;
                        right: 0;
                        bottom: -10px;
                        content: '';
                        width: 100%;
                        height: 2px;
                        background: #f5564e;
                        margin: 0 auto;
                    }

                    .heading-section-white {
                        color: rgba(255, 255, 255, .8);
                    }

                    .heading-section-white h2 {
                        line-height: 1;
                        padding-bottom: 0;
                    }

                    .heading-section-white h2 {
                        color: #fff;
                    }

                    .heading-section-white .subheading {
                        margin-bottom: 0;
                        display: inline-block;
                        font-size: 13px;
                        text-transform: uppercase;
                        letter-spacing: 2px;
                        color: rgba(255, 255, 255, .4);
                    }

                    .call-to-action {
                        padding: 1em 2em;
                        background: #f06292;
                        color: #fff;
                        border-radius: 999px;
                    }
                </style>
            </head>

            <body width="100%" style="margin: 0; padding: 0 !important; mso-line-height-rule: exactly; background-color: #222;">
                <center style="width: 100%; background-color: #f1f1f1;">
                    <div
                        style="display: none; font-size: 1px;max-height: 0px; max-width: 0px; opacity: 0; overflow: hidden; mso-hide: all; font-family: sans-serif;">
                        &zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;
                    </div>
                    <div style="max-width: 600px; margin: 0 auto;" class="email-container">
                        <table align="center" role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%"
                            style="margin: auto;">
                            <tr>
                                <td valign="top" class="bg_white" style="padding: 1em 2.5em;">
                                    <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%">
                                        <tr>
                                            <td width="60%" class="logo" style="text-align: left;">
                                                <h1>
                                                    <a href="https://selfie2anime.com">
                                                        Selfie<span class="text_primary">2</span>Anime&nbsp;<span
                                                            class="text_primary">アニメ</span>
                                                    </a>
                                                </h1>
                                            </td>
                                            <td width="40%" class="logo" style="text-align: right;">
                                                <a href="https://www.facebook.com/sharer/sharer.php?u=https://selfie2anime.com">
                                                    <img width="32" height="32" src="https://selfie2anime.com/email/facebook.png"
                                                        alt="Share on Facebook">
                                                </a>
                                                <a href="https://twitter.com/intent/tweet?url=https://selfie2anime.com&text=What do YOU look like in anime?&hashtags=selfie2anime"
                                                    target="_blank">
                                                    <img width="32" height="32" src="https://selfie2anime.com/email/twitter.png"
                                                        alt="Share on Twitter">
                                                </a>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                            <tr>
                                <td valign="middle" class="bg_white" style="padding: 80px 0;">
                                    <div class="overlay"></div>
                                    <table>
                                        <tr>
                                            <td>
                                                <div class="text" style="text-align: center; margin: 0 20px">
                                                    Your verification token was invalid.
                                                </div>

                                                <div class="text" style="font-size: 10px; text-align: center; margin: 0 50px">
                                                    Make sure you clicked the delete image button from the email you received. If that doesn't work, contact us at <a href="mailto:legal@selfie2anime.com">legal@selfie2anime.com</a> to have your data removed another way.</div>
                                                </div>

                                                <div class="text" style="text-align: center; margin: 4em 0">
                                                    <a href="https://selfie2anime.com/" class="call-to-action">
                                                        GENERATE ANOTHER ONE!
                                                    </a>
                                                </div>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                            <tr>
                                <td valign="middle" class="bg_primary"
                                    style="background-image: url(https://selfie2anime.com/email/wall.jpg); background-size: cover; height: 480px;">
                                </td>
                            </tr>
                            <tr>
                                <td class="bg_dark email-section" style="text-align:center;">
                                    <div class="heading-section heading-section-white">
                                        <p>
                                            Copyright &copy; 2019-2020 by
                                            <a href="https://selfie2anime.com">Selfie2Anime.com</a>
                                        </p>
                                    </div>
                                </td>
                            </tr>
                        </table>
                    </div>
                </center>
            </body>
            </html>
            """

    response = {
        "statusCode": 200,
        "body": html_body,
        "headers": {
            'Content-Type': 'text/html',
        }
    }

    return response
