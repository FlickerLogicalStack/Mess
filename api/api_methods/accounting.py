from . import os, json, hashlib
from . import csrf_exempt, authenticate, JsonResponse, MinimumLengthValidator, CommonPasswordValidator, NumericPasswordValidator, ValidationError, timezone
from . import User, Profile, File, Token, websocket_socket_notify, redis_server

@csrf_exempt
def register(request):
	params = json.loads(request.body.decode("utf-8"))

	email = params["email"]
	username = params["username"]
	password = params["password"]

	if Profile.objects.filter(user__email=email).count() or Profile.objects.filter(user__username=username).count():
		return JsonResponse({"ok": False, "error": "Profile with such 'email' or/and 'username' already exist"})

	for validator in [MinimumLengthValidator(), CommonPasswordValidator(), NumericPasswordValidator()]:
		try:
			validator.validate(params["password"])
		except ValidationError as e:
			return JsonResponse({"ok": False, "error": e.messages[0]})

	new_user = User.objects.create_user(username=username, password=password, email=email)

	new_profile = Profile.objects.create(
		user=new_user,
		display_name=params.get("display_name", ""))

	if params.get("avatar_id") is not None:
		try:
			avatar = File.objects.get(id=params["avatar_id"])
		except File.DoesNotExist:
			return JsonResponse({"ok": False, "error": "No file with such id for avatar"})

		if avatar.is_avatarable:
			new_puddle.avatar = avatar
		else:
			return JsonResponse({"ok": False, "error": "File with such id not avatarable"})

	return JsonResponse({"ok": True, "profile": new_profile.as_json()})

@csrf_exempt
def generate_token(request):
	params = json.loads(request.body.decode("utf-8"))

	authenticated_user = authenticate(request,
		username=params["username"],
		password=params["password"]
	)

	if not authenticated_user:
		return JsonResponse({"ok": False, "message": "Wrong username/password data"})

	token_string = hashlib.md5(os.urandom(256)).hexdigest()

	profile = Profile.objects.get(user=authenticated_user)
	
	try:
		token = Token.objects.get(profile=profile)
	except Token.DoesNotExist:
		token = Token.objects.create(profile=profile, token=token_string)
	else:
		token.token = token_string
		token.save()

	return JsonResponse({"ok": True, "token": token_string, "username": profile.user.username})

@csrf_exempt
def set_password(request):
	params = json.loads(request.body.decode("utf-8"))

	try:
		profile = Token.objects.get(token=params["token"]).profile
	except Token.DoesNotExist:
		return JsonResponse({"ok": False, "error": "Wrong token"})
	else:
		profile.last_activity = timezone.now()
		profile.save()

	if not profile.user.check_password(params["old_password"]):
		return JsonResponse({"ok": False, "error": "Wrong old password"})

	for validator in [MinimumLengthValidator(), CommonPasswordValidator(), NumericPasswordValidator()]:
		try:
			validator.validate(params["password"])
		except ValidationError as e:
			return JsonResponse({"ok": False, "error": e.messages[0]})

	profile.user.set_password(params["password"])
	profile.user.save()

	return JsonResponse({"ok": True})

def get_profile(request):
	params = request.GET

	try:
		profile = Token.objects.get(token=params["token"]).profile
	except Token.DoesNotExist:
		return JsonResponse({"ok": False, "error": "Wrong token"})
	else:
		profile.last_activity = timezone.now()
		profile.save()

	try:
		requested_profile = Profile.objects.get(user__username=params["username"])
	except Profile.DoesNotExist:
		return JsonResponse({"ok": False, "error": "No user with such username"})

	return JsonResponse({"ok": True, "profile": requested_profile.as_json()})

@csrf_exempt
def add_friend(request):
	params = json.loads(request.body.decode("utf-8"))

	try:
		profile = Token.objects.get(token=params["token"]).profile
	except Token.DoesNotExist:
		return JsonResponse({"ok": False, "error": "Wrong token"})
	else:
		profile.last_activity = timezone.now()
		profile.save()

	try:
		profile2 = Profile.objects.get(user__username=params["username"])
	except Profile.DoesNotExist:
		return JsonResponse({"ok": False, "error": "No profile with such username"})
	
	profile.friends.add(profile2)

	websocket_socket_notify(
		redis_server.get(profile.user.id),
		profile2,
		"add",
		{"profile": profile2.as_json()})

	return JsonResponse({"ok": True})

@csrf_exempt
def remove_friend(request):
	params = json.loads(request.body.decode("utf-8"))

	try:
		profile = Token.objects.get(token=params["token"]).profile
	except Token.DoesNotExist:
		return JsonResponse({"ok": False, "error": "Wrong token"})
	else:
		profile.last_activity = timezone.now()
		profile.save()

	try:
		profile2 = profile.friends.all().get(user__username=params["username"])
	except Profile.DoesNotExist:
		return JsonResponse({"ok": False, "error": "You have not friend with such username"})
	
	profile.friends.remove(profile2)

	return JsonResponse({"ok": True})