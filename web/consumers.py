from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from core.models import Profile, Message
from api.models import Token

import json
from pprint import pprint
import redis

redis_server = redis.StrictRedis(host='localhost', port=6379, db=0)

class MainConsumer(WebsocketConsumer):
    def connect(self):
        self.is_auth = False
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            self.send(text_data='{"ok": false, "error": "JSONDecodeError"}')
            return

        if data.get("type"):
            if data["type"] == "messageRead":
                if data.get("message_id"):
                    try:
                        message = Message.objects.get(id=data["message_id"])
                    except Message.DoesNotExist:
                        self.send(text_data='{"ok": false}')
                    else:
                        try:
                            profile = Token.objects.get(token=self.scope["url_route"]["kwargs"]["token"]).profile
                        except Token.DoesNotExist:
                            self.send(text_data='{"ok": false}')
                        else:
                            message.readed_by.add(profile)
                            self.send(text_data='{"ok": true}')

            elif data["type"] == "auth" and not self.is_auth:
                if data.get("token"):
                    try:
                        profile = Token.objects.get(token=data["token"]).profile
                    except Token.DoesNotExist:
                        self.send({"error": "Wrong token"})
                    else:
                        redis_server.set(profile.user.id, self.channel_name)
                        self.is_auth = True
                        self.send(text_data='{"ok": true}')

        print("Receive:", data)

    def event_handler(self, event):
        data = {
            "container": event.get("container", {}),
            "sender": event.get("sender", "Unknown"),
            "type": event.get("event_type", "Unknown"),
        }

        self.send(text_data=json.dumps(data))