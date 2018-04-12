
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import never_cache, cache_page

from .models import File, Puddle, Profile, Message

import os.path

@cache_page(604800)
def get_file(request, file_id):
	file = get_object_or_404(File, id=file_id).file

	if os.path.isfile(file.path):
		with open(file.path, 'rb') as f:
			response = HttpResponse(f.read())
			response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file.name)
			return response
			