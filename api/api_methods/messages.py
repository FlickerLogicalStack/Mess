from . import json
from . import JsonResponse, csrf_exempt, timezone
from . import Token, File, Message, Puddle, websocket_socket_notify, redis_server

@csrf_exempt
def send_message(request):
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

	files = []
	for file_id in params.get("files", []):
		try:
			file = File.objects.get(id=file_id)
		except File.DoesNotExist:
			return JsonResponse({"ok": False, "error": "No file with such id"})
		else:
			if file.owner_profile.id != profile.id:
				return JsonResponse({"ok": False, "error": "No file with such id uploaded by you"})
		files.append(file)

	fmessages = []
	for message_id in params.get("forwarded", []):
		try:
			fmessage = Message.objects.get(id=message_id)
		except Message.DoesNotExist:
			return JsonResponse({"ok": False, "error": "No message with such id"})

		try:
			profile.puddles.all().get(id=fmessage.target_puddle.id)
		except puddle.DoesNotExist:
			return JsonResponse({"ok": False, "error": "You don't know message with such id"})
		fmessages.append(fmessage)

	if not (params.get("text", "") or files or fmessages):
		return JsonResponse({"ok": False, "error": "New message must have text, file or forwarded message"})

	new_message = Message(
		profile=profile,
		target_puddle=puddle,
		text=params.get("text", ""))

	new_message.save()

	new_message.files.set(files)
	new_message.forwarded_messages.set(fmessages)
	new_message.readed_by.add(profile)

	for member in new_message.target_puddle.members.all():
		websocket_socket_notify(
			redis_server.get(member.user.id),
			new_message,
			"new",
			{"message": new_message.as_json()})

	return JsonResponse({"ok": True, "message": new_message.as_json()})

@csrf_exempt
def edit_message(request):
	params = json.loads(request.body.decode("utf-8"))

	try:
		profile = Token.objects.get(token=params["token"]).profile
	except Token.DoesNotExist:
		return JsonResponse({"ok": False, "error": "Wrong token"})
	else:
		profile.last_activity = timezone.now()
		profile.save()

	try:
		message = Message.objects.get(id=params["id"])
	except Message.DoesNotExist:
		return JsonResponse({"ok": False, "error": "No message with such id"})

	try:
		profile.puddles.all().get(id=message.target_puddle.id)
	except Puddle.DoesNotExist:
		return JsonResponse({"ok": False, "error": "You don't know message with such id"})

	if message.profile != profile:
		return JsonResponse({"ok": False, "error": "You can't edit non-yours message"})

	if (timezone.now() - message.timestamp).days:
		return JsonResponse({"ok": False, "error": "Too late for editing"})
	
	message.text = params["text"]
	message.edited = True

	message.save()

	for member in message.target_puddle.members.all():
		websocket_socket_notify(
			redis_server.get(member.user.id),
			message,
			"edit",
			{"message": message.as_json()})

	return JsonResponse({"ok": True, "message": message.as_json()})

@csrf_exempt
def delete_message(request):
	params = json.loads(request.body.decode("utf-8"))

	try:
		profile = Token.objects.get(token=params["token"]).profile
	except Token.DoesNotExist:
		return JsonResponse({"ok": False, "error": "Wrong token"})
	else:
		profile.last_activity = timezone.now()
		profile.save()

	try:
		message = Message.objects.get(id=params["id"])
	except Message.DoesNotExist:
		return JsonResponse({"ok": False, "error": "No message with such id"})
	
	message.not_show_for.add(profile)

	for member in message.target_puddle.members.all():
		websocket_socket_notify(
			redis_server.get(member.user.id),
			message,
			"delete",
			{"message": message.as_json()})

	return JsonResponse({"ok": True})

def get_unreaded(request):
	params = request.GET

	try:
		profile = Token.objects.get(token=params["token"]).profile
	except Token.DoesNotExist:
		return JsonResponse({"ok": False, "error": "Wrong token"})
	else:
		profile.last_activity = timezone.now()
		profile.save()

	messages = [msg.as_json() for msg in profile.unreaded_messages]
	if len(messages) > 50:
		messages = messages[:50]

	return JsonResponse({"ok": True, "messages": messages})
