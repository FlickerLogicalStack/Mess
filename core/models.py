import os
import datetime
import hashlib
import json
import fleep

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.utils import timezone

def space_separated(value):
	if value.strip("0123456789 "):
		raise ValidationError(
			_('"%(value)s" contain non-digit and "space" symbols: "%(striped)s"'),
			params={'value': value, 'striped': value.strip("0123456789 ")},
		)

def md5hash_filename(instance, filename):
	now = timezone.now()
	return os.path.join(str(now.year), str(now.month), str(now.day),
		f"{hashlib.md5(os.urandom(512)).hexdigest()}.{filename.rsplit('.', 1)[-1]}")

class File(models.Model):
	owner = models.ForeignKey("Profile", on_delete=models.SET_NULL, null=True)
	file = models.FileField(upload_to=md5hash_filename)
	mime = models.CharField(max_length=32, blank=True)
	file_hash = models.CharField(max_length=32, blank=True)

	def save(self, *args, **kwargs):
		info = fleep.get(self.file.file.file.read(86))
		mime = info.mime[0] if info.mime else "application/octet-stream"
		self.mime = mime

		file_hash = hashlib.md5(self.file.file.read()).hexdigest()

		existing_files = File.objects.filter(file_hash=file_hash)
		if existing_files:
			self.file = existing_files.first().file

		self.file_hash = file_hash

		super(File, self).save(*args, **kwargs)

class Message(models.Model):
	sender = models.ForeignKey("Profile", on_delete=models.SET_NULL, null=True)
	target_puddle = models.ForeignKey("Puddle", on_delete=models.SET_NULL, null=True)
	timestamp = models.DateTimeField(default=timezone.now)

	text = models.CharField(max_length=1024, blank=True, db_index=True)
	files = models.ManyToManyField("File", blank=True)
	forwarded = models.ManyToManyField("Message", blank=True)

	readed_by = models.TextField(validators=[space_separated])
	hidden_from = models.ManyToManyField("Profile", blank=True, related_name="hidden_from")

	edited = models.BooleanField(default=False)

	class Meta:
		ordering = ["-timestamp"]

	def __str__(self):
		return f"{self.__class__.__name__}({self.id})"

class Puddle(models.Model):
	creator = models.ForeignKey("Profile", on_delete=models.SET_NULL, null=True, related_name="creator")
	# LMAO FIELDS SYNCING (LOOK AT 'Profile') AHHAHAHAHHHAHAHAHHAHAHHA
	# users = models.ManyToManyField("Profile", blank=True)
	# OMG I'M SO STUPID AHHAHAHAHHAHAHHAHAHAHHAHAHHA
	# WELL, LETS CREATE SOME PROPERTY AHAHHAHAHHAHHAHAHHAHHA
	messages = models.ManyToManyField("Message", blank=True)

	title = models.CharField(max_length=128, blank=True)
	avatar = models.ForeignKey("File", on_delete=models.SET_NULL, null=True, blank=True)

	def __str__(self):
		return f"{self.__class__.__name__}({self.id})"

	@property
	def last_message(self):
		return self.messages.all().first()

	@property
	def users(self):
		return self.profile_set

	def unreaded_count_by(self, profile):
		return self.messages.all().exclude(readed_by__regex=f"(?:\A| ){profile.id}(?: |\Z)").count()

class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True)
	puddles = models.ManyToManyField("Puddle", blank=True)
	friends = models.ManyToManyField("self", blank=True)
	friend_requests = models.ManyToManyField("Profile", blank=True)

	fullname = models.CharField(max_length=128, blank=True)
	avatar = models.ForeignKey("File", on_delete=models.SET_NULL, null=True, blank=True)
	bio = models.CharField(max_length=128, blank=True)
	
	last_activity = models.DateTimeField(default=timezone.now)

	def __str__(self):
		return f"{self.__class__.__name__}({self.user})"