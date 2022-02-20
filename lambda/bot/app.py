import os
import json
import boto3

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, ImageMessage, TextSendMessage
)

import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

channel_secret = <your secret>
channel_access_token = <your access token>

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)


@handler.add(MessageEvent, message=TextMessage)
def message_text(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='STARTボタンを押して猫の写真を送ってね❗️とある猫の種類をあてちゃうよ♪')
    )

def query_endpoint(img):
    endpoint_name = <your model endpoint>
    client = boto3.client('runtime.sagemaker')
    response = client.invoke_endpoint(EndpointName=endpoint_name, ContentType='application/x-image', Body=img, Accept='application/json;verbose')
    return response
    
def parse_prediction(query_response):
    model_predictions = json.loads(query_response['Body'].read())
    predicted_label = model_predictions['predicted_label']
    labels = model_predictions['labels']
    probabilities = model_predictions['probabilities']
    return predicted_label, probabilities, labels 

@handler.add(MessageEvent, message=ImageMessage)
def message_image(event):
    ## https://github.com/line/line-bot-sdk-python#get_message_contentself-message_id-timeoutnone
    message_id = event.message.id
    
    message_content = line_bot_api.get_message_content(message_id)
    
    tmp_file_path = '/tmp/image.jpg'
    
    with open(tmp_file_path, 'wb') as fd:
        for chunk in message_content.iter_content():
            fd.write(chunk)
            
    img = bytes()
    with open(tmp_file_path, 'rb') as file:
        img = file.read()
            
    query_response = query_endpoint(img)
    predicted_label, probabilities, labels = parse_prediction(query_response)
            
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=f'ふむふむこのネコの種類は...💡 ズバリ【{predicted_label}】という種類のネコだにゃん😸')
    )

def lambda_handler(event, context):
    # get X-Line-Signature header value
    signature = event["headers"]["x-line-signature"]

    # get request body as text
    body = event["body"]
    logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.error("Got exception from LINE Messaging API")

    ## https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html        
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": ""
    }