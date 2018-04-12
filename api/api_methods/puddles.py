from . import os, json, hashlib
from . import csrf_exempt, authenticate, JsonResponse, timezone
from . import User, Profile, File, Token, Puddle

def get_puddle_messages(request):
	params = request.GET

	try:
		profile = Token.objects.get(token=params["token"]).profile
	except Token.DoesNotExist:
		return JsonResponse({"ok": False, "error": "Wrong token"})
	else:
		profile.last_activity = timezone.now()
		profile.save()

	puddle_id = params.get("puddle_id")
	offset = int(params.get("offset", 0))
	count = int(params.get("count", 25))
	reversed_ = int(params.get("reversed", 0))

	try:
		puddle = profile.puddles.get(id=puddle_id)
	except Puddle.DoesNotExist:
		return JsonResponse({"ok": False, "error": "You have not puddle with such id"})

	messages = []
	for message in puddle.messages.all().order_by("-timestamp" if not reversed_ else "timestamp")[offset:offset+count]:
		if profile.user.username not in [i.user.username for i in message.not_show_for.all()]:
			messages.append(message.as_json())

	return JsonResponse({"ok": True, "messages": messages})

def get_puddle(request):
	params = request.GET

	try:
		profile = Token.objects.get(token=params["token"]).profile
	except Token.DoesNotExist:
		return JsonResponse({"ok": False, "error": "Wrong token"})
	else:
		profile.last_activity = timezone.now()
		profile.save()

	try:
		puddle = profile.puddles.get(id=params["puddle_id"])
	except Puddle.DoesNotExist:
		return JsonResponse({"ok": False, "error": "You have not puddle with such id"})

	return JsonResponse({"ok": True, "puddle": puddle.as_json()})

def get_puddles(request):
	params = request.GET
	
	try:
		profile = Token.objects.get(token=params["token"]).profile
	except Token.DoesNotExist:
		return JsonResponse({"ok": False, "error": "Wrong token"})
	else:
		profile.last_activity = timezone.now()
		profile.save()

	count = int(params.get("count", 25))
	offset = int(params.get("offset", 0))
	reversed_ = int(params.get("reversed_", 0))

	puddles = []
	for puddle in profile.puddles.all()[offset:offset+count]:
		if profile.user.username not in [i.user.username for i in puddle.not_show_for.all()]:
			puddles.append(puddle.as_json())
	
	return JsonResponse({"ok": True, "puddles": puddles})

@csrf_exempt
def create_puddle(request):
	params = json.loads(request.body.decode("utf-8"))

	params["users"] = list(set(params["users"]))

	if not len(set(params["users"])):
		return JsonResponse({"ok": False, "error": "Puddle must have at least 1 other user"})

	try:
		profile = Token.objects.get(token=params["token"]).profile
	except Token.DoesNotExist:
		return JsonResponse({"ok": False, "error": "Wrong token"})
	else:
		profile.last_activity = timezone.now()
		profile.save()

	users = profile.friends.filter(user__username__in=params["users"])

	if profile.mutually_friends.intersection(users).filter(id__in=users).count() != len(params["users"]):
		return JsonResponse({"ok": False, "error": "You can't invire non-friend users"})

	new_puddle = Puddle.objects.create(
		creator=profile,
		display_name=params.get("display_name", ""))

	new_puddle.members.set(users)
	new_puddle.members.add(profile)

	if params.get("avatar_id") is not None:
		try:
			avatar = File.objects.get(id=params["avatar_id"])
		except File.DoesNotExist:
			return JsonResponse({"ok": False, "error": "No file with such id for avatar"})

		if avatar.is_avatarable:
			new_puddle.avatar = avatar
		else:
			return JsonResponse({"ok": False, "error": "File with such id not avatarable"})

	for member in new_puddle.members.all():
		member.puddles.add(new_puddle)

	return JsonResponse({"ok": True, "puddle": new_puddle.as_json()})

@csrf_exempt
def delete_puddle(request):
	params = json.loads(request.body.decode("utf-8"))

	try:
		profile = Token.objects.get(token=params["token"]).profile
	except Token.DoesNotExist:
		return JsonResponse({"ok": False, "error": "Wrong token"})
	else:
		profile.last_activity = timezone.now()
		profile.save()

	try:
		puddle = profile.puddles.get(id=params["puddle_id"])
	except Puddle.DoesNotExist:
		return JsonResponse({"ok": False, "error": "You have not puddle with such id"})

	puddle.not_show_for.add(profile)

	return JsonResponse({"ok": True})

@csrf_exempt
def edit_puddle(request):
	params = json.loads(request.body.decode("utf-8"))

	try:
		profile = Token.objects.get(token=params["token"]).profile
	except Token.DoesNotExist:
		return JsonResponse({"ok": False, "error": "Wrong token"})
	else:
		profile.last_activity = timezone.now()
		profile.save()

	try:
		puddle = profile.puddles.all().get(id=params["puddle_id"])
	except Puddle.DoesNotExist:
		return JsonResponse({"ok": False, "error": "You have not puddle with such id"})

	display_name = params.get("display_name")
	avatar_id = params.get("avatar_id")

	if display_name is None:
		puddle.display_name = ""
	else:
		puddle.display_name = display_name

	try:
		avatar = File.objects.get(id=avatar_id)
	except File.DoesNotExist:
		return JsonResponse({"ok": False, "error": "No file with such id"})

	puddle.avatar = avatar

	puddle.save()

	return JsonResponse({"ok": True, "puddle": puddle.as_json()})

@csrf_exempt
def add_users_to_puddle(request):
	params = json.loads(request.body.decode("utf-8"))

	try:
		profile = Token.objects.get(token=params["token"]).profile
	except Token.DoesNotExist:
		return JsonResponse({"ok": False, "error": "Wrong token"})
	else:
		profile.last_activity = timezone.now()
		profile.save()

	try:
		puddle = profile.puddles.get(id=params["puddle_id"])
	except Puddle.DoesNotExist:
		return JsonResponse({"ok": False, "error": "You have not puddle with such id"})

	users = profile.friends.filter(user__username__in=params["users"])

	if profile.mutually_friends.intersection(users).filter(id__in=users).count() != len(params["users"]):
		return JsonResponse({"ok": False, "error": "You can't invite non-friend users"})

	puddle.members.add(*users)

	# MEGA SLOW ACTIONS
	# CAN'T USE UPDATE CAUSE M2M FIELD
	for message in puddle.messages.all():
		message.readed_by.add(*users)

	return JsonResponse({"ok": True, "puddle": puddle.as_json()})

@csrf_exempt
def remove_users_from_puddle(request):
	params = json.loads(request.body.decode("utf-8"))

	try:
		profile = Token.objects.get(token=params["token"]).profile
	except Token.DoesNotExist:
		return JsonResponse({"ok": False, "error": "Wrong token"})
	else:
		profile.last_activity = timezone.now()
		profile.save()

	try:
		puddle = profile.puddles.get(id=params["puddle_id"])
	except Puddle.DoesNotExist:
		return JsonResponse({"ok": False, "error": "You have not puddle with such id"})

	users = profile.friends.filter(user__username__in=params["users"])

	puddle.members.remove(*users)

	return JsonResponse({"ok": True, "puddle": puddle.as_json()})