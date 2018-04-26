import json
import hashlib
import os
import rest_framework
import redis
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from django.apps import apps
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import MinimumLengthValidator, CommonPasswordValidator, NumericPasswordValidator
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone

from api.serializers import ProfileSerializer, SelfProfileSerializer, PuddleSerializer, MessageSerializer, FileSerializer
from api.models import Token

Profile = apps.get_model("core", "Profile")
Puddle = apps.get_model("core", "Puddle")
Message = apps.get_model("core", "Message")
File = apps.get_model("core", "File")

redis_server = redis.StrictRedis(host="localhost", port=6379, db=0)


def websocket_socket_notify(channel_name, sender, event_type, container):
    if channel_name is None:
        return

    if isinstance(channel_name, bytes):
        channel_name = channel_name.decode("utf-8")

    async_to_sync(get_channel_layer().send)(
        channel_name, {
            "type": "event_handler",
            "sender": sender,
            "event_type": event_type,
            "container": container,
        }
    )


def BadJsonResponse(error_msg):
    return JsonResponse({"ok": False, "error": error_msg})


def GoodJsonResponse(data=None, extra=None, extra_per_object=None):
    response = {"ok": True}
    if data:
        if isinstance(data, rest_framework.serializers.BaseSerializer):
            if isinstance(data, rest_framework.serializers.ListSerializer):
                response.update({"result": data.data})
            else:
                response.update({"result": [data.data]})
        else:
            if isinstance(data, (list, tuple, set)):
                response.update({"result": data})
            else:
                response.update({"result": [data]})

    if extra is not None:
        response.update(extra)

    if extra_per_object is not None:
        for i in range(len(response["result"])):
            response["result"][i].update(extra_per_object[i])

    return JsonResponse(response)


def puddle_notify(profile, type, data):
    websocket_socket_notify(
        redis_server.get(profile.id),
        "Puddle",
        type,
        data)


def profile_notify(profile, type, username):
    websocket_socket_notify(
        redis_server.get(profile.id),
        "Profile",
        type,
        {"profile_username": username})
