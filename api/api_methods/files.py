from . import csrf_exempt, HttpResponse, JsonResponse, timezone
from . import File, Token

@csrf_exempt
def upload_file(request):
	params = request.POST

	try:
		profile = Token.objects.get(token=params["token"]).profile
	except Token.DoesNotExist:
		return JsonResponse({"ok": False, "error": "Wrong token"})
	else:
		profile.last_activity = timezone.now()
		profile.save()

	new_file = File(
		owner_profile=profile,
		file=request.FILES["file"])
	new_file.save()

	return JsonResponse({"ok": True, "file": new_file.as_json()})

def download_file(request):
	params = request.GET

	try:
		profile = Token.objects.get(token=params["token"]).profile
	except Token.DoesNotExist:
		return JsonResponse({"ok": False, "error": "Wrong token"})
	else:
		profile.last_activity = timezone.now()
		profile.save()

	try:
		file = File.objects.get(id=params["id"])
	except File.DoesNotExist:
		return JsonResponse({"ok": False, "error": "No file with such id"})
	else:
		response = HttpResponse(file.file.file.read(), content_type=file.mime)
		response['Content-Disposition'] = 'inline; filename=' + file.file.name
		return response
