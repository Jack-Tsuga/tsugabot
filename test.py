# coding=utf-8

# インポートするライブラリ
from datetime import datetime


from flask import Flask, request, abort, render_template, g,jsonify

"""

from linebot import (

    LineBotApi, WebhookHandler
)

from linebot.exceptions import (

    InvalidSignatureError
)

from linebot.models import (

    FollowEvent, MessageEvent, TextMessage, TextSendMessage, ImageMessage, ImageSendMessage, TemplateSendMessage,

    ButtonsTemplate, PostbackTemplateAction, MessageTemplateAction, URITemplateAction, FlexSendMessage, PostbackAction,

    MessageAction, URIAction, QuickReplyButton, QuickReply
)

"""

import base64

from io import BytesIO

from PIL import Image

#from hamlish_jinja import HamlishExtension

#from werkzeug import ImmutableDict


#from flask                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             _sqlalchemy import SQLAlchemy
import sqlalchemy     # salalchemy 小文字じゃないとエラー

def jls_extract_def():
    # テストデータ用
    return 


import glob # テストデータ用 = jls_extract_def()

import os

from psycopg2.extras import psycopg2,DictCursor

#import sys

import json



# 軽量なウェブアプリケーションフレームワーク:Flask

app = Flask(__name__)

app.config['JSON_AS_ASCII'] = False #jason dump defaultの英文字設定をやめて、日本語表示可とする



# 環境変数からLINE Access Tokenを設定

#LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]

# 環境変数からLINE Channel Secretを設定

#LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]

# 環境変数からDATABASE_URLを読み込む

# DATABASE_URL = os.environ.get('DATABASE_URL')

DATABASE_URL ="postgresql://postgres:tfxYR#6fnKGGaWr@db.yzkqvvmfbrmxdugyxafq.supabase.co:5432/postgres"



# データベース読み込みクラス ---------------------

class db_obj():

  def __init__(self):

    self.conn = psycopg2.connect(DATABASE_URL)	# データベース接続
 

  def __enter__(self):
    return self
 

  def call(self, sql):	# sqlを実行

    cur = self.conn.cursor(cursor_factory=DictCursor)	# DictCursor: 辞書型でデータを返す
    

    cur.execute(sql)

    return(cur.fetchall())	# 結果を返す
 

  def __exit__(self, exception_type, exception_value, traceback):

    self.conn.close()



SQL = 'SELECT * FROM shops'		# 店の全リストを選択


with db_obj() as conn :

    cur = conn.call(SQL)

    shops=cur


print(type(cur))

for data in cur:

  print(data['name'])