import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer


class Player(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        print(self.room_name)
        self.room_group_name = 'chat_%s' % self.room_name
        print(self.room_group_name)

        # joining the room
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        print(self.scope['user'])

    async def disconnect(self, code):
        # leve the room
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # receive message from websocket
    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # send message to websocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
