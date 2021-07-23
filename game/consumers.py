from channels.generic.websocket import AsyncWebsocketConsumer
# from django.contrib.auth.models import User
from .models import Character
from channels.db import database_sync_to_async
import json
import random


online_users = []


def find_id(new_id=0):
    new_id = new_id
    found = False

    while found is False:
        temp = False
        for user in online_users:
            if user.user_id == new_id:
                temp = True
                break
        if temp is False:
            return new_id
        else:
            new_id += 1


class GameUser:

    def __init__(self, name, user_id, channel_name):
        self.user_id = user_id
        self.owner = name
        self.channel_name = channel_name
        self.character_name = ''
        self.pos_x = 0
        self.pos_y = 0

        self.character_stats = {}
        self.group = name + '_group'

        self.state = 'idle'
        self.direction = 'down'

        self.max_health = 100
        self.current_health = 100
        self.skin = None

        self.fight_group = ''

    def get_user_name(self):
        return str(self.owner)

    def set_character_name(self, new_name):
        self.character_name = new_name
        self.group = new_name + '_group'

    def update_pos(self, x=None, y=None):
        if x is not None:
            self.pos_x = x
        if y is not None:
            self.pos_y = y

    def get_position(self):
        r = {
            'player_name': self.owner,
            'character_name': self.character_name,
            'position': {
                'x': self.pos_x,
                'y': self.pos_y
            },
            'state': self.state,
            'direction': self.direction
        }
        return r

    def get_info(self):
        info = {
            'id': self.user_id,
            'owner': self.owner,
            'character_name': self.character_name,
            'character_stats': self.character_stats,
            'pos': {
                'x': self.pos_x,
                'y': self.pos_y
            },
            'skin': self.skin
        }
        return info


class GameConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        self.group_name = 'test_game'

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

        new_id = find_id()
        print('id for ' + self.scope['user'].username + ': ' + str(new_id))
        new_user = GameUser(self.scope['user'].username, new_id, self.channel_name)
        online_users.append(new_user)

    async def disconnect(self, code):

        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

        user_to_remove = self.get_user_by_name()

        if user_to_remove.character_name != '':
            await self.channel_layer.group_send(
                self.group_name, {
                    'type': 'data.message',
                    'message': {
                        'action': 'remove_user',
                        'data': {
                            'user_to_remove': user_to_remove.get_info()
                        }
                    }
                }
            )

        user_n = self.get_user_number()
        online_users.pop(user_n)
        display_online_users()

    async def data_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({'message': message}))

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        action = data['action']

        # JOIN SERVER
        if action == 'join_server':
            user = self.get_user_by_name(data['player_name'])
            pos = data['position']
            user.update_pos(pos['x'], pos['y'])
            user.set_character_name(data['character_name'])

            info = await database_sync_to_async(find_character)(data['character_name'])
            user.character_stats = info['stats']
            user.skin = info['skin']

            await self.channel_layer.group_add(
                user.group,
                self.channel_name
            )

            other_users = []
            for other_user in online_users:
                if user.owner != other_user.owner and other_user.character_name != '':
                    other_users.append(other_user.get_info())

            if len(other_users) == 0:
                other_users = 'u are alone :)'

            await self.channel_layer.group_send(
                self.group_name, {
                    'type': 'data.message',
                    'message': {
                        'action': 'new_user_joined',
                        'data': {
                            'new_user': user.get_info(),
                            'other_users': other_users,
                        }
                    }
                }
            )
            display_online_users()
        # MOVEMENT
        elif action == 'position_update':
            character_name = data['character_name']
            user = get_user_by_character_name(character_name)
            position = data['position']
            user.update_pos(position['x'], position['y'])
            user.state = data['state']
            user.direction = data['direction']

            await self.channel_layer.group_send(
                self.group_name, {
                    'type': 'data.message',
                    'message': {
                        'action': 'position_update',
                        'data': {
                            'user_to_update': user.get_position()
                        }
                    }
                }
            )
        # FIGHT REQUEST
        elif action == 'fight_request':
            other_user = data['to']['player']
            other_user_o = self.get_user_by_name(other_user)
            await self.channel_layer.group_send(
                other_user_o.group, {
                    'type': 'data.message',
                    'user': self.scope['user'].username,
                    'message': {
                        'action': 'fight_request',
                        'data': {
                            'from': {
                                'player': data['from']['player'],
                                'character': data['from']['character']
                            },
                            'text': ['wants to fight'],
                            'buttons': {
                                'true': 'accept',
                                'false': 'decline'
                            }
                        }
                    }
                }
            )
        # FIGHT START
        elif action == 'fight_start':
            player_0 = data['text']['player_0']
            player_1 = data['text']['player_1']

            p_0 = self.get_user_by_name(player_0['player'])
            p_1 = self.get_user_by_name(player_1['player'])

            p_0.update_pos(240, 240)
            p_1.update_pos(400, 240)

            fight_group_name = p_0.character_name + '_' + p_1.character_name + '_fight_group'
            p_0.fight_group = fight_group_name
            p_1.fight_group = fight_group_name

            # if p_1.owner == self.scope['user'].username:
            #     await self.channel_layer.group_add(
            #         p_0.group,
            #         self.channel_name
            #     )
            await self.channel_layer.group_add(
                fight_group_name,
                p_0.channel_name
            )

            await self.channel_layer.group_add(
                fight_group_name,
                p_1.channel_name
            )

            # await self.channel_layer.group_send(
            #     fight_group_name, {
            #         'type': 'data.message',
            #         'message': {
            #             'action': 'test',
            #             'data': {
            #                 'text': 'u are in fight group: ' + fight_group_name
            #             }
            #         }
            #     }
            # )

            await self.channel_layer.group_send(
                self.group_name, {
                    'type': 'data.message',
                    'message': {
                        'action': 'fight_between',
                        'data': {
                            'group_name': fight_group_name,
                            'player_0': p_0.get_info(),
                            'player_1': p_1.get_info(),
                            'first_move': random.randint(0, 1)
                        }
                    }
                }
            )
        # FIGHT MOVE
        elif action == 'fight_move':
            group = data['data']['group_name']
            await self.channel_layer.group_send(
                group, {
                    'type': 'data.message',
                    'message': {
                        'action': 'fight_move',
                        'data': {
                            'player': self.scope['user'].username,
                            'player_move': data['data']['player_move']
                        }
                    }
                }
            )
        # FIGHT END
        elif action == 'fight_end':
            # group = data['data']['group_name']
            # print('test: ' + str(data))
            print('test:\n' + self.scope['user'].username)
            print(self.channel_name)

            p_0 = get_user_by_character_name(data['data']['player_0'])
            p_1 = get_user_by_character_name(data['data']['player_1'])

            await self.channel_layer.group_discard(
                p_0.fight_group,
                p_0.channel_name
            )

            await self.channel_layer.group_discard(
                p_1.fight_group,
                p_1.channel_name
            )

            await self.channel_layer.group_send(
                self.group_name, {
                    'type': 'data.message',
                    'message': {
                        'action': 'fight_end',
                        'data': {
                            'player_0': data['data']['player_0'],
                            'player_1': data['data']['player_1'],
                            'winner': data['data']['winner']
                        }
                    }
                }
            )
        # ADD CHARACTER
        elif action == 'add_character':
            print('\n')
            user = self.get_user_by_name()
            exists = await database_sync_to_async(self.add_character)(data)
            message = {
                'type': 'data.message',
                'message': {
                    'action': 'add_character',
                    'data': {
                        'available': False,
                        'text': 'username is not available'
                    }
                }
            }
            if exists is False:
                message['message']['data']['text'] = 'character created'
                message['message']['data']['available'] = True
                user.skin = data['skin']
                user.character_stats = data['stats']
                user.set_character_name(data['name'])
            print('add test: ' + str(user.get_info()))

            await self.channel_layer.group_add(
                user.group,
                self.channel_name
            )

            await self.channel_layer.group_send(
                user.group, message
            )

    def get_user_by_name(self, name=None):
        if name is None:
            name = self.scope['user'].username
        for user in online_users:
            if user.owner == name:
                return user

    def get_user_number(self, name=None):
        if name is None:
            name = self.scope['user'].username

        n = 0
        for user in online_users:
            if user.owner == name:
                return n
            n += 1

    def add_character(self, data):
        exists = False
        characters = Character.objects.all()
        for character in characters:
            if character.name == data['name']:
                exists = True
                break

        if exists is False:
            print('character created')
            Character.objects.create(owner=self.scope['user'],
                                     name=data['name'],
                                     texture=data['skin'],
                                     strength=data['stats']['strength'],
                                     agility=data['stats']['agility'],
                                     attack=data['stats']['attack'],
                                     defense=data['stats']['defense'],
                                     vitality=data['stats']['vitality'],
                                     charisma=data['stats']['charisma'],
                                     stamina=data['stats']['stamina'],
                                     magick=data['stats']['stamina'])
        return exists


def find_character(name):
    characters = Character.objects.all()
    for ch in characters:
        if ch.name == name:
            return ch.get_info()


def get_user_by_character_name(character_name):
    for user in online_users:
        if user.character_name == character_name:
            return user


def display_online_users():
    n = 1
    character = 'still thinking'
    print('online users:')
    for user in online_users:
        if user.character_name != '':
            character = user.character_name
        print(str(n) + '. player: ' + user.owner + ', character: ' + character + ', id: ' + str(user.user_id))
        n += 1
