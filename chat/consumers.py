import json
from channels.generic.websocket import AsyncWebsocketConsumer


# ChatConsumerクラス: WebSocketからの受け取ったものを処理するクラス
class ChatConsumer(AsyncWebsocketConsumer):

    # WebSocket接続時の処理
    async def connect(self):
        # グループに参加
        self.strGroupName = 'chat'
        await self.channel_layer.group_add(self.strGroupName, self.channel_name)

        # WebSocket接続を受け入れます。
        # ・connect()でaccept()を呼び出さないと、接続は拒否されて閉じられます。
        # 　たとえば、要求しているユーザーが要求されたアクションを実行する権限を持っていないために、接続を拒否したい場合があります。
        # 　接続を受け入れる場合は、connect()の最後のアクションとしてaccept()を呼び出します。
        await self.accept()

    # WebSocket切断時の処理
    async def disconnect(self, close_code):
        # グループから離脱
        await self.channel_layer.group_discard(self.strGroupName, self.channel_name)

    # WebSocketからのデータ受信時の処理
    # （ブラウザ側のJavaScript関数のsocketChat.send()の結果、WebSocketを介してデータがChatConsumerに送信され、本関数で受信処理します）
    async def receive(self, text_data):
        # 受信データをJSONデータに復元
        text_data_json = json.loads(text_data)

        # メッセージの取り出し
        strMessage = text_data_json['message']
        # グループ内の全コンシューマーにメッセージ拡散送信（受信関数を'type'で指定）
        data = {
            'type': 'chat_message', # 受信処理関数名
            'message': strMessage, # メッセージ
        }
        await self.channel_layer.group_send(self.strGroupName, data)

    # 拡散メッセージ受信時の処理
    # （self.channel_layer.group_send()の結果、グループ内の全コンシューマーにメッセージ拡散され、各コンシューマーは本関数で受信処理します）
    async def chat_message(self, data):
        data_json = {
            'message': data['message'],
        }

        # WebSocketにメッセージを送信します。
        # （送信されたメッセージは、ブラウザ側のJavaScript関数のsocketChat.onmessage()で受信処理されます）
        # JSONデータをテキストデータにエンコードして送ります。
        await self.send(text_data=json.dumps(data_json))
