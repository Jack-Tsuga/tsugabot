# coding=utf-8
# インポートするライブラリ
from datetime import datetime

from flask import Flask, request, abort, render_template, g,jsonify

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

import base64
from io import BytesIO
from PIL import Image
#from hamlish_jinja import HamlishExtension
#from werkzeug import ImmutableDict

from flask_sqlalchemy import SQLAlchemy

import glob # テストデータ用

import os
from psycopg2.extras import psycopg2,DictCursor
#import sys
import json


# 軽量なウェブアプリケーションフレームワーク:Flask
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False #jason dump defaultの英文字設定をやめて、日本語表示可とする


# 環境変数からLINE Access Tokenを設定
LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
# 環境変数からLINE Channel Secretを設定
LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]
# 環境変数からDATABASE_URLを読み込む
DATABASE_URL = os.environ.get('DATABASE_URL')

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handle = WebhookHandler(LINE_CHANNEL_SECRET)

# データベース読み込みクラス ---------------------
class db_obj():
  def __init__(self):
    self.conn = psycopg2.connect(DATABASE_URL)	# データベース接続
 
  def __enter__(self):
    return self
 
  def call_select(self, sql):	# sqlを実行
    cur = self.conn.cursor(cursor_factory=DictCursor)	# DictCursor: 辞書型でデータを返す
    
    cur.execute(sql)
    return(cur.fetchall())	# 結果を返す
  
  def call_any(self, sql):	# sqlを実行
    cur = self.conn.cursor()
    cur.execute(sql)
    return(cur)	# 結果を返す

   
  def __exit__(self, exception_type, exception_value, traceback):
    self.conn.close()

#----------------------------------------------
@app.route("/")
def index():
	moji = u"こんにちは、ビ研です"

	return "<h1>Tsugabot Home test cut handler</h1>"

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handle.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@app.route("/custmr")
def custmr():
	moji = u"こんにちは、ビ研です"

	return render_template("/custmr/index.html",moji=moji)

@app.route("/custmr/order", methods=['POST'])
def order():
	data_text=""
	order_data = {}	# 予約(注文）商品のリスト
	product_id =[]	# 商品番号
	product_name=[]	# 商品名
	price=[]	# 商品単価
	quantity=[]	# 商品個数
	total=[]	# 金額：商品毎の単価×数量＝金額
	grand_total = 0 # 合計金額
	order_number = 0 # 予約（注文）番号

	if request.method == 'GET':
		# quantity = request.args.get('quantity[]')
		quantity = request.args.getlist('quantity')
	elif request.method == 'POST':
		product_id = request.form.getlist('product_id')
		product_name= request.form.getlist('product_name')
		price= request.form.getlist('price')
		quantity = request.form.getlist('quantity')
	
	
	grand_total = 0
	for p , q in zip(price,quantity):
		t = int(p) * int(q)	# 単価×数量＝合計金額
		grand_total += t	# 総合計に加算
		total.append(t)		# 商品毎の金額を配列に保存

	# 注文内容をorder_data変数にまとめる
	order_data ={'product_id': product_id , 'product_name':product_name, 'price': price , 'quatity': quantity , 'total' : total}	
		


	# 予約(注文）内容を保存する

	
	return render_template("/custmr/order.html",order_numer=order_number,order_data=order_data,grand_total=grand_total)

@app.route("/auth")
def auth():
	moji = u"Loginしてください"

	return render_template("/auth/index.html",moji=moji)

@app.route("/mngmt")
def mngmt():
	moji = u"こんにちは、ビ研です"

	return render_template("/mngmt/index.html",moji=moji)

@app.route("/mngmt/orderlist")
def orderlist():
	moji = u"こんにちは、ビ研です"

	return render_template("/mngmt/orderlist.html",moji=moji)

@app.route("/mngmt/orderdtl", methods=['GET'])
def orderdtl():
	if request.method == 'GET':
		id = request.args.get('orderid')
	elif request.method == 'POST':
		id = request.form['orderid']


	# テストデータ
	items =[{"id": 101, "name": 'イチゴショートケーキ', "shopname": 'ケーキ屋アンナ', "price": "250", "quantity": "1", "total": "250"},
			{"id": 201, "name": 'チョコラ', "shopname": '函大ケーキ', "price": "100", "quantity": "2", "total": "200"},
			{"id": 112, "name": 'マロングラッセ', "shopname": '高丘菓子店', "price": "200", "quantity": "5", "total": "1000"},
			{"id": 234, "name": 'シュークリーム', "shopname": 'ケーキ屋アンナ', "price": "150", "quantity": "3", "total": "450"},
			{"id": 678, "name": 'ロールケーキ', "shopname": 'ケーキ屋アンナ', "price": "550", "quantity": "1", "total": "550"}]

	#テストデータの合計金額の計算（あとで不要かも？）
	GrandTotal = 10		# 総合計を初期化
	for item in items:
		print(item)
		GrandTotal += int(item["total"])

	name = "花子"
	orderdate = "2022/05/17 15:15"

	return render_template("/mngmt/orderdtl.html",orderid=id,name=name,date=orderdate,products=items,GrandTotal=GrandTotal)

@app.route("/mngmt/orderdtl_resp", methods=['GET'])
def orderdtl_resp():
	if request.method == 'GET':
		id = request.args.get('orderid')
		command = request.args.get('command')
	elif request.method == 'POST':
		id = request.form['orderid']
		command = request.form['command']

	if command == "1" :
		# 引渡し済みのデータベース処理
		cmd=1
	elif command == "2" :
		# 予約取り消しのデータベース処理
		cmd=2
	else:
		cmd=-1
	

	name = "花子"
	orderdate = "2022/05/17 15:15"

	return render_template("/mngmt/orderdtl_resp.html",orderid=id,name=name,date=orderdate,command=cmd)

@app.route("/mngmt/shoplist")
def shoplist():
	
	SQL = 'SELECT * FROM shops order by "id" '		# 店の全リストを選択

	with db_obj() as conn :
		cur = conn.call_select(SQL)
		shops=cur


	return render_template("/mngmt/shoplist.html",shops=shops)

@app.route("/mngmt/shop_resp", methods=['post'])
def shop_resp():
	command = "0"	# コマンドを初期化
	id = -1 	# 主キー（店番号を初期化）
	if request.method == 'GET':
		id = request.args.get('id')
		command = request.args.get('command')
	elif request.method == 'POST':
		id = request.form['id']
		command = request.form['command']
		name = request.form['name']
		yomi = request.form['yomi']
		staff = request.form['staff']
		tel = request.form['tel']

	if command == "1" :
		# 新規登録データベース処理
		SQL = "INSERT INTO shops (name,yomi,staff,tel) VALUES ('"+name+"','"+yomi+"','"+staff+"','"+tel+"');"	# 店の全リストを選択

		with db_obj() as conn :
			cur = conn.call_any(SQL)
			id = cur.execute("select lastval() from shops")
			

	elif command == "2" :
		# のデータベース処理
		cmd=2
	elif command == "99" :
		# のデータベース処理
		cmd=2
	else:
		cmd=-1
	
	status = 0;	#　データベースアクセス結果の情報　
	name = "花子"
	orderdate = "2022/05/17 15:15"

	return render_template("/mngmt/shop_resp.html",shopid=id,status=status)

@app.route("/mngmt/productlist")
def productlist():
	# テスト画像データ（本来は、データベースから読み込む
	files = glob.glob("static/custmr/images/*.jpg")


	image_b64data=[]	# テスト用画像配列

	for i,file in enumerate(files):
		img = Image.open(file)
		buffer = BytesIO()
		img.save(buffer, "jpeg")
		image_b64str = base64.b64encode(buffer.getvalue()).decode("utf-8") 
	#	return "<p>"+ image_b64str+"</p>"
	# image要素のsrc属性に埋め込めこむために、適切に付帯情報を付与する
		image_b64data.append("data:image/jpeg;base64,{}".format(image_b64str) )



	# テストデータ
	items =[{"id": 101,"image_b64data":image_b64data[0],"name": '苺ショートケーキ', "yomi": "いちごしょーとけーき", "shop": "ケーキ屋アンナ", "price": "250", "stock": "50"},
			{"id": 201,"image_b64data":image_b64data[1],"name": 'ショコラ', "yomi": "しょおこら", "shop": "函大ケーキ", "price": "300", "stock": "2"},
			{"id": 112,"image_b64data":image_b64data[2],"name": 'レアチーズケーキ', "yomi": "れあちーずけーき", "shop": "セラーム菓子店", "price": "200", "stock": "10"},
			{"id": 3,"image_b64data":image_b64data[3],"name": '洋なしのチーズタルト', "yomi": "ようなしのちーずたると", "shop": "高丘菓子店", "price": "230", "stock": "3"},
			{"id": 434,"image_b64data":image_b64data[4],"name": 'レモンのタルト', "yomi": "れもんのたると", "shop": "ケーキ屋アンナ", "price": "180", "stock": "12"},
			{"id": 214,"image_b64data":image_b64data[5],"name": 'モンブラン', "yomi": "もんぶらん", "shop": "高丘菓子店", "price": "220", "stock": "20"},
			{"id": 334,"image_b64data":image_b64data[6],"name": 'チョコレートケーキ', "yomi": "ちょこれーとけーき", "shop": "ケーキ屋アンナ", "price": "450", "stock": "15"},
			{"id": 123,"image_b64data":image_b64data[7],"name": 'シュークリーム', "yomi": "しゅーくりーむ", "shop": "和将ケーキ店", "price": "400", "stock": "50"},
			{"id": 234,"image_b64data":image_b64data[8],"name": '苺ショートケーキ', "yomi": "いちごしょーとけーき", "shop": "函大ケーキ", "price": "380", "stock": "32"},
			{"id": 234,"image_b64data":image_b64data[9],"name": 'シュークリーム', "yomi": "しゅーくりーむ", "shop": "セラーム菓子店", "price": "290", "stock": "3"},
			{"id": 234,"image_b64data":image_b64data[10],"name": 'レアチーズケーキ', "yomi": "れあちーずけーき", "shop": "和将ケーキ店", "price": "330", "stock": "6"},
			{"id": 234,"image_b64data":image_b64data[11],"name": 'ショコラ', "yomi": "しょおこら", "shop": "和将ケーキ店", "price": "270", "stock": "40"},
			{"id": 678,"image_b64data":image_b64data[12],"name": 'モンブラン', "yomi": "もんぶらん", "shop": "高丘菓子店", "price": "220", "stock": "23"}]

	#return "<h1> test </h1>"+','.join(files) 
	return render_template("/mngmt/productlist.html",items=items)

@app.route("/mngmt/product_resp", methods=['POST'])
def product_resp():
	if request.method == 'GET':
		id = request.args.get('id')
		command = request.args.get('command')
	elif request.method == 'POST':
		id = request.form['id']
		command = request.form['command']
		image = request.files['item_img']
	image.save("test.jpg")

	if command == "1" :
		# 引渡し済みのデータベース処理
		cmd=1
	elif command == "2" :
		# 予約取り消しのデータベース処理
		cmd=2
	else:
		cmd=-1
	
	status = 0;	#　データベースアクセス結果の情報　
	name = "フルーツケーキ"
	date = "2022/05/17 15:15"
 	# 画像書き込み用バッファを確保して画像データをそこに書き込む
	#buf = BytesIO()
	# image.save(buf,format="jpeg")

    # バイナリデータをbase64でエンコードし、それをさらにutf-8でデコードしておく
	image_b64str = base64.b64encode(image.getvalue()).decode("utf-8") 
	
	# image要素のsrc属性に埋め込めこむために、適切に付帯情報を付与する
	image_b64data = "data:image/jpeg;base64,{}".format(image_b64str) 
	return render_template("/mngmt/product_resp.html",productid=id,name=name,image_b64data=image_b64data,date=date,command=command)


@app.route("/test", methods=['POST'])
def test():
	moji = u"こんにちは"
	if request.method == 'GET':
		msg1 = request.args.get('msg1')
		msg2 = request.args.get('msg2')
	elif request.method == 'POST':
		msg1 = request.form['msg1']
		msg2 = request.form['msg2']
		suji1 = int(msg1)
		suji2 = int(msg2)
		kotae = suji1 + suji2

	return render_template("test.html",moji1=msg1,moji2=msg2,kotae=kotae)

@app.route("/read_db")
def read_db():

	sql = 'SELECT * FROM studenttbl'
	# conn = db_obj()
	with db_obj() as conn :
		cur = conn.call(sql)

		msg = ""
		for row in cur:

			msg = msg + "<tr><td>"+str(row[0])+"</td><td>"+row[1]+"</td></tr>"

	kotae = msg
	return render_template("testdb.html",kotae=kotae)
#	return jsonify(res)

# MessageEvent
@handle.add(MessageEvent, message=TextMessage)
def handle_message(event):
	line_bot_api.reply_message(
        event.reply_token,
#        TextSendMessage(text=u"「" + event.message.text + u"」って何？AAAA")
#       TextSendMessage(text=zd.henji(event.message.text))
        [henji(event.message.text),
        qRepBtn()]
	)

# フォローイベントの場合の処理
@handle.add(FollowEvent)
def handle_follow(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='初めまして')
    )




def henji(msg):
	JsMsg=[]
	henjiMsg = ""
	henjiMsg = henjiMsg  + "\n" + msg + "\n" + "\n１．アットホームな大学で、教職員と学生が仲良しです。\n２．先輩とも仲良くなれるのが楽しいです。\n３．海外プロジェクトに参加すると海外の友達もできます"

	hmsg = TextSendMessage(text=henjiMsg)

	return hmsg

# ---------------------------------------
# QuickReplyButton テスト関数
# ---------------------------------------

def qRepBtn():
	
    language_list = ["セナ", "ゆうた", "若沢", "釜澤", "津金","アンナ"]

    items = [QuickReplyButton(action=MessageAction(label=f"{language}", text=f"{language}が好き")) for language in language_list]

    msg = TextSendMessage(text="誰が好きですか？ ",quick_reply=QuickReply(items=items))

    return msg

# ----------------------------------------

if __name__ == "__main__":
    port = int(os.getenv("PORT"))
    app.run(host="0.0.0.0", port=port,debug=True)
