import time

from . import csrf_exempt, redis_server, websocket_socket_notify
from . import File, Profile, Puddle, PuddleSerializer, MessageSerializer, BadJsonResponse, GoodJsonResponse

def puddle_notify(profile, type, data):
    websocket_socket_notify(
        redis_server.get(profile.id),
        "Puddle",
        type,
        data)

def get_puddle(request):
    profile = request.META["profile"]

    try:
        puddle = profile.puddles.all().get(id=request.META["params"]["puddle_id"])
    except Puddle.DoesNotExist:
        return BadJsonResponse("No puddle with such id")

    serializer = PuddleSerializer(puddle)

    extra_per_object = [{"unreaded_count": puddle.unreaded_count_by(profile)}]

    return GoodJsonResponse(serializer, extra_per_object=extra_per_object)

def get_puddles(request):
    profile = request.META["profile"]
    count = int(request.META["params"].get("count", 50))
    offset = int(request.META["params"].get("offset", 0))
    reversed_ = int(request.META["params"].get("reversed", 0))

    all_puddles = profile.puddles.all()

    all_puddles = sorted(all_puddles,
        key=lambda puddle: time.mktime(puddle.last_message.timestamp.timetuple()) if puddle.last_message else puddle.id, reverse=True)

    if reversed_:
        all_puddles = list(reversed(all_puddles))

    puddles_count = len(all_puddles)

    if offset > puddles_count:
        puddles = []
    else:
        if offset+count > puddles_count:
            puddles = all_puddles[offset:]
        else:
            puddles = all_puddles[offset:(offset+count)]

    serializer = PuddleSerializer(puddles, many=True)

    extra_per_object = [{"unreaded_count": p.unreaded_count_by(profile)} for p in puddles]

    return GoodJsonResponse(serializer, extra={"next": offset+count}, extra_per_object=extra_per_object)

def get_puddle_messages(request):
    profile = request.META["profile"]
    count = int(request.META["params"].get("count", 50))
    offset = int(request.META["params"].get("offset", 0))
    reversed_ = int(request.META["params"].get("reversed", 0))

    try:
        puddle = profile.puddles.all().get(id=request.META["params"]["puddle_id"])
    except Puddle.DoesNotExist:
        return BadJsonResponse("No puddle with such id")

    all_messages = puddle.messages.all().exclude(
        hidden_from__in=[profile.id]).order_by("timestamp" if reversed_ else "-timestamp")[offset:count+offset]

    serializer = MessageSerializer(all_messages, many=True)

    # DON'T LOOK AT NEXT LINE
    extra_per_object = [{"readed": puddle.messages.all().filter(id=msg.id).filter(readed_by__regex=f"(?:\\A| ){profile.id}(?: |\\Z)").exists()} for msg in all_messages]
    # THANKS

    return GoodJsonResponse(serializer, extra={"next": offset+count}, extra_per_object=extra_per_object)

@csrf_exempt
def create_puddle(request):
    profile = request.META["profile"]
    users = request.META["params"]["users"]
    title = request.META["params"].get("title", None)
    avatar_id = request.META["params"].get("avatar_id", None)

    if not len([i for i in users if i != profile.user.username]):
        return BadJsonResponse("Puddle must have at least 1 other user")

    users_ = profile.friends.filter(user__username__in=users)
    if profile.friends.intersection(users_).filter(user__username__in=users).count() != len(users):
        return BadJsonResponse("You can't invite non-friend users")

    new_puddle = Puddle.objects.create(
        creator=profile,
        title=title or "")

    new_puddle.users.set(profile.friends.filter(user__username__in=users))
    new_puddle.users.add(profile)

    profile.puddles.add(new_puddle)

    if avatar_id is not None:
        try:
            new_puddle.avatar = File.objects.get(id=avatar_id)
        except File.DoesNotExist:
            pass

    for user in new_puddle.users.all():
        puddle_notify(user, "create", {"puddle": PuddleSerializer(new_puddle).data})

    return GoodJsonResponse(PuddleSerializer(new_puddle))

@csrf_exempt
def delete_puddle(request):
    profile = request.META["profile"]
    puddle_id = request.META["params"]["puddle_id"]

    try:
        puddle = profile.puddles.all().get(id=puddle_id)
    except Puddle.DoesNotExist:
        return BadJsonResponse("No puddle with such id")

    profile.puddles.remove(puddle)

    return GoodJsonResponse()

@csrf_exempt
def edit_puddle(request):
    profile = request.META["profile"]
    puddle_id = request.META["params"]["puddle_id"]
    title = request.META["params"].get("title", None)
    avatar_id = request.META["params"].get("avatar_id", None)

    if (title is None) and (avatar_id is None):
        return BadJsonResponse("Method must contain text or/and avarat_id")

    try:
        puddle = profile.puddles.all().get(id=puddle_id)
    except Puddle.DoesNotExist:
        return BadJsonResponse("No puddle with such id")

    if profile != puddle.creator:
        return BadJsonResponse("Only puddle's creator can edit puddle")

    if title is not None:
        puddle.title = title
        puddle.save()

    if avatar_id is not None:
        try:
            avatar = File.objects.get(id=avatar_id)
        except File.DoesNotExist:
            return BadJsonResponse("No file with such id")

        if avatar.owner != profile:
            return BadJsonResponse("You can use only self uploaded files by id")

        puddle.avatar = avatar

    for user in puddle.users.all():
        puddle_notify(user, "edit", {"puddle": PuddleSerializer(puddle).data})

    return GoodJsonResponse(PuddleSerializer(puddle))

@csrf_exempt
def add_users_to_puddle(request):
    profile = request.META["profile"]
    puddle_id = request.META["params"]["puddle_id"]
    users = request.META["params"]["users"]

    try:
        puddle = profile.puddles.all().get(id=puddle_id)
    except Puddle.DoesNotExist:
        return BadJsonResponse("No puddle with such id")

    users_ = profile.friends.all().filter(user__username__in=users)
    if profile.friends.intersection(users_).filter(user__username__in=users).count() != len(users):
        return BadJsonResponse("You can't invite non-friend users")

    puddle.users.add(*users_)

    for user in users_:
        puddle_notify(user, "invite", {"puddle": PuddleSerializer(puddle).data})

    return GoodJsonResponse(PuddleSerializer(puddle))

@csrf_exempt
def remove_users_from_puddle(request):
    profile = request.META["profile"]
    puddle_id = request.META["params"]["puddle_id"]
    users = request.META["params"]["users"]

    try:
        puddle = profile.puddles.all().get(id=puddle_id)
    except Puddle.DoesNotExist:
        return BadJsonResponse("No puddle with such id")

    if profile != puddle.creator:
        return BadJsonResponse("Only puddle's creator can kick users")

    for user in users:
        try:
            puddle.users.all().get(user__username=user)
        except Profile.DoesNotExist:
            return BadJsonResponse(f"Profile {user} not in your puddle")

    for user in puddle.users.all().filter(user__username__in=users):
        user.puddles.remove(puddle)
        puddle_notify(user, "kick", {"puddle": PuddleSerializer(puddle).data})

    for user in puddle.users.all():
        puddle_notify(user, "kick", {"puddle": PuddleSerializer(puddle).data})

    return GoodJsonResponse(PuddleSerializer(puddle))
