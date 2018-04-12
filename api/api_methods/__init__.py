import os

from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.core.files.storage import default_storage
from django.core.files import File
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.apps import apps
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib.auth.password_validation import MinimumLengthValidator, CommonPasswordValidator, NumericPasswordValidator

from api.models import Token

import datetime
from urllib.parse import unquote
from pprint import pprint
import json
import hashlib

import fleep
import redis
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

Profile = apps.get_model("web_mess", "Profile")
Puddle = apps.get_model("web_mess", "Puddle")
Message = apps.get_model("web_mess", "Message")
File = apps.get_model("web_mess", "File")

redis_server = redis.StrictRedis(host="localhost", port=6379, db=0)

def websocket_socket_notify(channel_name, sender, event_type, container):
	if channel_name is None:
		return

	if isinstance(channel_name, bytes):
		channel_name = channel_name.decode("utf-8")

	async_to_sync(get_channel_layer().send)(
		channel_name, {
			"type": "event_handler",
			"sender": sender.__class__.__name__,
			"event_type": event_type,
			"container": container,
			}
		)