import os.path
import json

from django.conf import settings
from django.apps import apps
from django.http import JsonResponse
from django.utils import timezone

from .utils import base_validation, check_request_params, profile_from_token
from .models import Token

class ApiRequestValidatorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        with open("api\methods.json") as file:
            self.METHODS_CONFIG = json.loads(file.read())

    def __call__(self, request):
        # IS THIS API REQUEST?
        if not request.path.startswith("/api/"):
            return self.get_response(request)

        # WAT THE API METHOD?
        method = request.path.replace("/api/", "")
        method_config = self.METHODS_CONFIG.get(method, None)
        if method_config is None:
            return JsonResponse({"ok": False, "error": f"Unknown api method '{method}'"})

        required_content_type = method_config.get("content_type", None)
        if (required_content_type is not None) and (request.content_type != required_content_type):
            return JsonResponse({"ok": False, "error": f"'content_type' must be '{required_content_type}'"})
        
        # IS REQUEST METHOD RIGHT?
        required_request_method = method_config.get("methods", ["GET", "POST"])
        if request.method not in required_request_method:
            return JsonResponse({"ok": False, "error": f"Wrong request method ({request.method.upper()}), must be in'{required_request_method}'"})

        # DECODE OR DIE
        if request.method == "POST":
            if request.content_type == "application/json":
                try:
                    params = json.loads(request.body.decode("utf-8"))
                except json.decoder.JSONDecodeError as json_decode_error:
                    return JsonResponse({"ok": False, "error": "JSONDecodeError: "+str(json_decode_error)})
                except Exception as e:
                    return JsonResponse({"ok": False, "error": e})
            else:
                params = dict(request.POST.items())
                params.update(dict(request.FILES.items()))
        elif request.method == "GET":
            params = request.GET

        # LAST VALIDATE ON PARAMS
        ok, error = check_request_params(params,
            method_config.get(request.method, {}).get("mandatory", []),
            method_config.get(request.method, {}).get("optional", []))
        if not ok:
            return JsonResponse({"ok":False, "error": error})
        else:
            request.META["params"] = params

        # FIND PROFILE BY TOKEN IF IT NEED
        if method_config.get("require_token", False):
            profile = profile_from_token(params["token"])
            if profile is None:
                return JsonResponse({"ok": False, "error": "Wrong token: " + params["token"]})
            request.META["profile"] = profile
            profile.last_activity = timezone.now()
            profile.save()

        response = self.get_response(request)

        return response