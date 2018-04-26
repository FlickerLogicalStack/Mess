from . import json, hashlib, os
from . import csrf_exempt, authenticate, ValidationError, MinimumLengthValidator, CommonPasswordValidator, NumericPasswordValidator, Q, User
from . import File, Profile, ProfileSerializer, SelfProfileSerializer, Puddle, PuddleSerializer, Message, MessageSerializer, Token, BadJsonResponse, GoodJsonResponse, redis_server, websocket_socket_notify, profile_notify


@csrf_exempt
def register(request):
    username = request.META["params"]["username"]
    email = request.META["params"]["email"]
    password = request.META["params"]["password"]

    if Profile.objects.filter(Q(user__username=username) | Q(user__email=email)).exists():
        return BadJsonResponse("Profile with such email or username already exist")

    for validator in [
            MinimumLengthValidator(),
            CommonPasswordValidator(),
            NumericPasswordValidator()]:
        try:
            validator.validate(password)
        except ValidationError as e:
            return BadJsonResponse(e.messages[0])

    new_user = User.objects.create_user(
        username=username, email=email, password=password)

    new_profile = Profile.objects.create(user=new_user)

    return GoodJsonResponse(SelfProfileSerializer(new_profile))


@csrf_exempt
def generate_token(request):
    username = request.META["params"]["username"]
    password = request.META["params"]["password"]

    authenticated_user = authenticate(request,
                                      username=username, password=password)

    if not authenticated_user:
        return BadJsonResponse("Wrong username/password data")

    token_string = hashlib.md5(os.urandom(1024)).hexdigest()

    profile = Profile.objects.get(user=authenticated_user)

    try:
        token = Token.objects.get(profile=profile)
    except Token.DoesNotExist:
        token = Token.objects.create(profile=profile, token=token_string)
    else:
        token.token = token_string
        token.save()

    return GoodJsonResponse({"token": token_string, "username": profile.user.username})


@csrf_exempt
def terminate_token(request):
    profile = request.META["profile"]

    Token.objects.filter(profile=profile).delete()

    return GoodJsonResponse()


@csrf_exempt
def set_password(request):
    profile = request.META["profile"]
    password = request.META["params"]["password"]

    if not profile.user.check_password(password):
        return BadJsonResponse("Wrong old password")

    for validator in [
            MinimumLengthValidator(),
            CommonPasswordValidator(),
            NumericPasswordValidator()]:
        try:
            validator.validate(password)
        except ValidationError as e:
            return BadJsonResponse(e.messages[0])

    profile.user.set_password(password)
    profile.user.save()

    return GoodJsonResponse()


def get_profile(request):
    username = request.META["params"]["username"]

    try:
        profile = Profile.objects.get(user__username=username)
    except Profile.DoesNotExist:
        return BadJsonResponse({"error": "No profile with such username"})

    if request.META["profile"] == profile:
        serializer = SelfProfileSerializer(profile)
    else:
        serializer = ProfileSerializer(profile)

    return GoodJsonResponse(serializer)


@csrf_exempt
def edit_profile(request):
    profile = request.META["profile"]

    avatar_id = request.META["params"].get("avatar_id", None)
    bio = request.META["params"].get("bio", None)
    fullname = request.META["params"].get("fullname", None)

    if (avatar_id is None) and (bio is None) and (fullname is None):
        return BadJsonResponse("Method must contain avatar_id or/and bio or/and fullname")

    if avatar_id is not None:
        try:
            avatar = File.objects.get(id=avatar_id)
        except File.DoesNotExist:
            return BadJsonResponse("No file with such id")

        if avatar.owner != profile:
            return BadJsonResponse("You can use only self uploaded files by id")

        profile.avatar = avatar

    if bio is not None:
        profile.bio = bio

    if fullname is not None:
        profile.fullname = fullname

    if (bio is not None) or (fullname is not None):
        profile.save()

    return GoodJsonResponse(SelfProfileSerializer(profile))


@csrf_exempt
def send_friend_request(request):
    profile = request.META["profile"]
    username = request.META["params"]["username"]

    try:
        another_profile = Profile.objects.get(user__username=username)
    except Profile.DoesNotExist:
        return BadJsonResponse("No profile with such username")

    if another_profile in profile.friends:
        return BadJsonResponse("This profile already in your friend list")

    another_profile.friend_requests.add(profile)

    profile_notify(another_profile, "send_friend_request",
                   profile.user.username)

    return GoodJsonResponse(ProfileSerializer(another_profile))


@csrf_exempt
def accept_friend_request(request):
    profile = request.META["profile"]
    username = request.META["params"]["username"]

    try:
        another_profile = profile.friend_requests.all().get(user__username=username)
    except Profile.DoesNotExist:
        return BadJsonResponse("No profile with such username in your friend requests list")

    profile.friend_requests.remove(another_profile)
    profile.friends.add(another_profile)
    another_profile.friends.add(profile)

    profile_notify(another_profile, "accept_friend_request",
                   profile.user.username)

    return GoodJsonResponse(ProfileSerializer(another_profile))


@csrf_exempt
def cancel_friend_request(request):
    profile = request.META["profile"]
    username = request.META["params"]["username"]

    try:
        another_profile = profile.friend_requests.all().get(user__username=username)
    except Profile.DoesNotExist:
        return BadJsonResponse("No your request in username's friend requests list")

    another_profile.friend_requests.remove(profile)

    profile_notify(another_profile, "cancel_friend_request",
                   profile.user.username)

    return GoodJsonResponse(ProfileSerializer(another_profile))


@csrf_exempt
def reject_friend_request(request):
    profile = request.META["profile"]
    username = request.META["params"]["username"]

    try:
        another_profile = profile.friend_requests.all().get(user__username=username)
    except Profile.DoesNotExist:
        return BadJsonResponse("No request from a such profile's username")

    profile.friend_requests.remove(another_profile)

    profile_notify(another_profile, "reject_friend_request",
                   profile.user.username)

    return GoodJsonResponse(ProfileSerializer(another_profile))


@csrf_exempt
def remove_friends(request):
    profile = request.META["profile"]
    users = request.META["params"]["users"]

    for user in users:
        try:
            profile.friends.all().get(user__username=user)
        except Profile.DoesNotExist:
            return BadJsonResponse(f"Profile {user} not in your friend list")

    profile.friends.remove(profile.friends.all().get(user__username__in=users))

    return GoodJsonResponse(users)
