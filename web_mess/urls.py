from django.urls import path

from . import views

app_name = "web_mess"

urlpatterns = [
	path("file/<int:file_id>", views.get_file, name="get_file"),
	]