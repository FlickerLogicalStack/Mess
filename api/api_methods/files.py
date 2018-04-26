from . import hashlib
from . import csrf_exempt, HttpResponse
from . import File, FileSerializer, BadJsonResponse, GoodJsonResponse

@csrf_exempt
def upload_file(request):
    profile = request.META["profile"]

    file = File.objects.create(
        owner=profile,
        file=request.FILES["file"])

    return GoodJsonResponse(FileSerializer(file))

@csrf_exempt
def download_file(request):
    profile = request.META["profile"]
    file_id = request.META["params"]["file_id"]

    try:
        file = File.objects.get(id=file_id)
    except File.DoesNotExist:
        return BadJsonResponse("No file with such id")

    if file.owner != profile:
        return BadJsonResponse("You can download only self uploaded files by id")

    response = HttpResponse(file.file.file.read(), content_type=file.mime)
    response['Content-Disposition'] = 'inline; filename=' + file.file.name
    return response
