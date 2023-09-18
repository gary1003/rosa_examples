import os
from linebot import LineBotApi
from linebot.models import TextSendMessage, TextMessage, MessageEvent, FollowEvent, UnfollowEvent, JoinEvent, LeaveEvent, PostbackEvent, BeaconEvent
from linebot import WebhookHandler
import boto3
from datetime import datetime
from uuid import uuid4

CHANNEL_SECRET = os.environ['CHANNEL_SECRET']
CHANNEL_ACCESS_TOKEN = os.environ['CHANNEL_ACCESS_TOKEN']
ACCESS_KEY = os.environ['AWS_ACCESS_KEY_ID_'] 
SECRET_KEY = os.environ['AWS_SECRET_ACCESS_KEY_']

# initialize line_bot_api to reply message
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
# initialize webhook handler to handle events
handler = WebhookHandler(CHANNEL_SECRET)

def lambda_handler(event_, context):
    signature = event_["headers"]["x-line-signature"]
    body = event_["body"]
    handler.handle(body, signature)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # add to dynamodb
    table = boto3.resource('dynamodb', region_name='ap-northeast-3', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY).Table('gary-rosa')
    Item = {
        'uuid': uuid4().hex, 'timestamp': str(event.timestamp), 
        'datetime': datetime.fromtimestamp(event.timestamp // 1000).strftime('%Y-%m-%d %H:%M:%S'),
        'source_type': event.source.type, 'user_id': event.source.user_id,
        'reply_token': event.reply_token, 
        'user_name': line_bot_api.get_profile(event.source.user_id).display_name,
        'group_id': event.source.group_id if event.source.type == 'group' else '',
        'group_name': line_bot_api.get_group_summary(event.source.group_id).group_name if event.source.type == 'group' else '',
        'room_id': event.source.room_id if event.source.type == 'room' else '',
        'room_name': line_bot_api.get_room_summary(event.source.room_id).room_name if event.source.type == 'room' else '',
        'message_type': event.message.type, 'message_text': event.message.text
    }

    table.put_item(Item=Item)
    # echo
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=event.message.text))

@handler.add(FollowEvent)
def handle_follow(event):
    # add to dynamodb
    table = boto3.resource('dynamodb', region_name='ap-northeast-3', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY).Table('gary-rosa-follower')
    Item = {
        'id': event.source.user_id, 'timestamp': str(event.timestamp),
        'datetime': datetime.fromtimestamp(event.timestamp // 1000).strftime('%Y-%m-%d %H:%M:%S'),
        'name': line_bot_api.get_profile(event.source.user_id).display_name,
        'reply_token': event.reply_token
    }
    table.put_item(Item=Item)
    # echo
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text='follow'))

@handler.add(UnfollowEvent)
def handle_unfollow(event):
    # delete from dynamodb
    table = boto3.resource('dynamodb', region_name='ap-northeast-3', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY).Table('gary-rosa-follower')
    try:
        table.delete_item(Key={'id': event.source.user_id})
    except:
        pass