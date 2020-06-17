# 自動發話
# -*- coding:utf-8-*-
# ./ngrok http 5000
import os

from bs4 import BeautifulSoup
from requests.auth import HTTPBasicAuth
import socket
from datetime import datetime
from email.mime.text import MIMEText
import smtplib
import atexit
import ssl
import os.path

import requests
from datetime import datetime

from flask import Flask, request, abort
import json
import time
import pandas as pd

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi(
    'XWhh1JWYRA4XBKHibrlc/3C0xWhtGT5QJ3sLRFdLaq6yJdlxBrbVSg5awtc8LdbBcGp5Daa8ZZt3GrKrg81PaEqi0xOpMoZ3YLNE8GoFpjfgRE5fMYRn1iEz6NUONmBDSqMdTeUTIZ5ymojLp8HWOgdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('11c8477ac81e82730baaa38d7312ea76')
user_id = 'Ub39505c0d61a045a0f0dc27aab13aa29'


dateTimeObj = datetime.now()
Realtime = dateTimeObj.strftime("%Y-%m-%d")

# 監聽所有來自 /callback 的 Post Request   
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    app.logger.info("signature : %s" % signature)
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Mark body: %s" % body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'ok'


@handler.add(MessageEvent)
def handle_message_test(event):
    # get user id when reply
    MessageType, UserId = getEventsData(event)  # 取得使用者的發送訊息類型以及Id
    getSendMessage = getUserSendMessage(
        event, message_type=MessageType)  # 回傳使用者輸入的文字訊息，如果不是文字就回傳None
    line_bot_api.reply_message(
        event.reply_token, TextSendMessage(getSendMessage))


def servercheck():
    url = 'https://scp.deltaww.com/ccm/service/com.ibm.team.process.internal.service.web.IProcessWebUIService/allProjectAreas?userId=clmadmin'
    r = requests.get(url, auth=HTTPBasicAuth('clmadmin', 'delta999'))
    sr = str(r)
    print("Web Requests responese:", sr)
    web = """%s- web status report :
    %s""" % (Realtime, sr)

    url2 = 'https://scp.deltaww.com/ccm/service/com.ibm.team.repository.service.internal.IServerStatusRestService/databaseStatus'
    r2 = requests.get(url2, auth=HTTPBasicAuth('clmadmin', 'delta999'))
    sr2 = str(r2)
    s2 = (sr2[11:14])
    sample2 = int(s2)

    if sample2 == 200:
        r = requests.get(url2, auth=HTTPBasicAuth('clmadmin', 'delta999'))
        soup = BeautifulSoup(r.text, "xml")
        code = soup.find('code').text
        print("Database status:", code)
        database = """DateBase status report-
        Status:%s""" % (code)

    result = """%s
    web status report :
    %s
    DateBase status report :%s
    """ % (Realtime, sr, code)

    return result


def getEventsData(event):
    """
    取得使用者輸入的訊息類型是什麼以及使用者的Id
    將這兩個參數值回傳
    """
    getMessageType = event.message.type
    getUserId = event.source.user_id
    app.logger.info("getMessageType: %s" % getMessageType)
    app.logger.info("getUserId: %s" % getUserId)
    return getMessageType, getUserId


def getUserSendMessage(event, message_type):
    # 使用者符合文字類型會將資訊回傳，如果不符合就會回傳None
    reply_message_str = '若要檢查RTC-Server狀態？請輸入\"檢查\"\n此機器人目前只能做以上功能，請見諒！'
    if message_type == 'text':
        app.logger.info("message content: %s" % event.message.text)
        if '檢查' in event.message.text:
            return servercheck()

    return reply_message_str


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
