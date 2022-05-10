import json
import datetime
from channels.generic.websocket import AsyncWebsocketConsumer

USERNAME_SYSTEM = '*system*'

# ChatConsumerクラス: WebSocketからの受け取ったものを処理するクラス
class ChatConsumer(AsyncWebsocketConsumer):
    
    # ルーム管理（クラス変数）
    rooms = None

    # コンストラクタ
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # クラス変数の初期化
        if ChatConsumer.rooms is None:
            ChatConsumer.rooms = {}

        self.strGroupName = ''
        self.strUserName = ''

    # WebSocket接続時の処理
    async def connect(self):
        # WebSocket接続を受け入れます。
        # ・connect()でaccept()を呼び出さないと、接続は拒否されて閉じられます。
        # 　たとえば、要求しているユーザーが要求されたアクションを実行する権限を持っていないために、接続を拒否したい場合があります。
        # 　接続を受け入れる場合は、connect()の最後のアクションとしてaccept()を呼び出します。
        await self.accept()

    # WebSocket切断時の処理
    async def disconnect(self, close_code):
        await self.leave_chat()

    # WebSocketからのデータ受信時の処理
    # （ブラウザ側のJavaScript関数のsocketChat.send()の結果、WebSocketを介してデータがChatConsumerに送信され、本関数で受信処理します）
    async def receive(self, text_data):
        # 受信データをJSONデータに復元
        text_data_json = json.loads(text_data)

        # チャットへの参加時処理
        if('join' == text_data_json.get('data_type')):
            # ユーザー名をクラスメンバー変数に設定
            self.strUserName = text_data_json['username']
            # チャットへの参加
            await self.join_chat()

        # チャットからの離脱時処理
        elif('leave' == text_data_json.get('data_type')):
            # チャットからの離脱
            await self.leave_chat()

        # メッセージ受診時処理
        else:
            # メッセージの取り出し
            strMessage = text_data_json['message']
            img_base64 = text_data_json['img_base64'] #img_base64の情報を追加
        # グループ内の全コンシューマーにメッセージ拡散送信（受信関数を'type'で指定）
            data = {
                'type': 'chat_message', # 受信処理関数名
                'message': strMessage, # メッセージ
                'img_base64' : img_base64, #image as binary
                'username' : self.strUserName, # ユーザー名
                'datetime' : datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'), # 現在時刻
            }
            await self.channel_layer.group_send(self.strGroupName, data)

            # logファイルの保存
            with open('chat.log', mode='a') as f:
                f.write(json.dumps(data)+'\n')
            	
    # 拡散メッセージ受信時の処理
    # （self.channel_layer.group_send()の結果、グループ内の全コンシューマーにメッセージ拡散され、各コンシューマーは本関数で受信処理します）
    async def chat_message(self, data):
        data_json = {
            'message' : data['message'],
            'img_base64' : data['img_base64'], #img_base64の情報を追加
            'username' : data['username'],
            'datetime' : data['datetime'],
        }

        # WebSocketにメッセージを送信します。
        # （送信されたメッセージは、ブラウザ側のJavaScript関数のsocketChat.onmessage()で受信処理されます）
        # JSONデータをテキストデータにエンコードして送ります。
        await self.send(text_data=json.dumps(data_json))

    async def join_chat(self):
        # グループに参加
        self.strGroupName = 'chat'
        await self.channel_layer.group_add(self.strGroupName, self.channel_name)
        
        # 参加人数の更新
        room = ChatConsumer.rooms.get(self.strGroupName)
        if(None == room):
            # ルーム管理にルームを追加
            ChatConsumer.rooms[self.strGroupName] = {'participants_count' : 1}
        else:
            room['participants_count'] += 1

        strMessage = '"' + self.strUserName + '" joined. There are ' + str(ChatConsumer.rooms[self.strGroupName]['participants_count']) + ' participants.'
        data = {
            'type' : 'chat_message',
            'message' : strMessage,
            'img_base64' : "", #img_base64の情報を追加,(system messageなので""でよい)
            'username' : USERNAME_SYSTEM,
            'datetime' : datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'),
        }

        # logを表示
        with open('chat.log', mode='a') as f:
            pass
        with open('chat.log') as f:
            tmp = f.readlines()
        for i in range(1,min(51,len(tmp))):
            await self.channel_layer.send(self.channel_name, json.loads(tmp[-(min(51,len(tmp))-i)]))

        # 入室システムメッセージを送信
        await self.channel_layer.group_send(self.strGroupName, data)


    # チャットから離脱
    async def leave_chat(self):
        if('' == self.strGroupName):
            return

        # グループから離脱
        await self.channel_layer.group_discard(self.strGroupName, self.channel_name)
        
        # 参加人数の更新
        ChatConsumer.rooms[self.strGroupName]['participants_count'] -= 1
        # システムメッセージ
        strMessage = '"' + self.strUserName + '" left. There are ' + str(ChatConsumer.rooms[self.strGroupName]['participants_count']) + ' participants.'
        # メッセージ送信
        data = {
            'type' : 'chat_message',
            'message' : strMessage,
            'img_base64' : "",#img_base64の情報を追加,(system messageなので""でよい)
            'username' : USERNAME_SYSTEM,
            'datetime' : datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'),
        }
        await self.channel_layer.group_send(self.strGroupName, data)

        if(0 == ChatConsumer.rooms[self.strGroupName]['participants_count']):
            del ChatConsumer.rooms[self.strGroupName]

        # ルーム名を空に
        self.strGroupName = ''
