from . import json
from . import csrf_exempt, timezone, redis_server, websocket_socket_notify
from . import Profile, ProfileSerializer, Puddle, PuddleSerializer, Message, File, MessageSerializer, BadJsonResponse, GoodJsonResponse

@csrf_exempt
def send_message(request):
    profile = request.META["profile"]

    text = request.META["params"]["text"]
    puddle_id = request.META["params"]["puddle_id"]
    files = request.META["params"]["files"]
    forwarded = request.META["params"]["forwarded"]

    if not (text or files or forwarded):
        return BadJsonResponse("Message must contain text or/and files or/and forwarded")

    try:
        puddle = profile.puddles.all().get(id=puddle_id)
    except Puddle.DoesNotExist:
        return BadJsonResponse("You haven't puddle with such id")

    message = Message.objects.create(
        sender=profile,
        target_puddle=puddle,
        text=text,
        )

    message.readed_by = f"{profile.id} "
    message.save()

    puddle.messages.add(message)

    for fmessage_id in forwarded:
        try:
            fmessage = Message.objects.get(id=fmessage_id)
        except Message.DoesNotExist:
            return BadJsonResponse(f"No message with such id ({fmessage_id})")
        message.forwarded.add(fmessage)

    for file_id in files:
        try:
            file = File.objects.get(id=file_id)
        except File.DoesNotExist:
            return BadJsonResponse(f"No file with such id ({file_id})")
        message.files.add(file)

    for user in puddle.users.all():
        websocket_socket_notify(
            redis_server.get(user.id),
            "Message",
            "new",
            {"message": MessageSerializer(message).data})

    return GoodJsonResponse(MessageSerializer(message))

@csrf_exempt
def edit_message(request):
    profile = request.META["profile"]

    puddle_id = request.META["params"]["puddle_id"]
    message_id = request.META["params"]["message_id"]
    text = request.META["params"]["text"]

    try:
        puddle = profile.puddles.all().get(id=puddle_id)
    except Puddle.DoesNotExist:
        return BadJsonResponse("You haven't puddle with such id")

    try:
        message = puddle.messages.all().get(id=message_id)
    except Message.DoesNotExist:
        return BadJsonResponse("You haven't message with such id")

    if message.sender != profile:
        return BadJsonResponse("You can't edit other's message")

    if (timezone.now() - message.timestamp).days:
        return BadJsonResponse("Too late for editing")
    
    message.text = text
    message.edited = True

    message.save()

    for user in puddle.users.all():
        websocket_socket_notify(
            redis_server.get(user.id),
            "Message",
            "edit",
            {"message": MessageSerializer(message).data})

    return GoodJsonResponse(MessageSerializer(message))

@csrf_exempt
def delete_message(request):
    profile = request.META["profile"]

    puddle_id = request.META["params"]["puddle_id"]
    message_id = request.META["params"]["message_id"]

    try:
        puddle = profile.puddles.all().get(id=puddle_id)
    except Puddle.DoesNotExist:
        return BadJsonResponse("You haven't puddle with such id")

    try:
        message = puddle.messages.all().get(id=message_id)
    except Message.DoesNotExist:
        return BadJsonResponse("You haven't message with such id")

    message.hidden_from.add(profile)

    return GoodJsonResponse()
