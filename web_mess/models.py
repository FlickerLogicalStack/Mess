from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.apps import apps

import json
import datetime

import fleep

from api.models import Token

class File(models.Model):
	owner_profile = models.ForeignKey("Profile", on_delete=models.SET_NULL, null=True)
	file = models.FileField()
	mime = models.CharField(max_length=32, null=True)

	@property
	def is_avatarable(self):
		return True

	def save(self, *args, **kwargs):
		info = fleep.get(self.file.file.file.read(64))
		mime = info.mime[0] if info.mime else "application/octet-stream"

		self.mime = mime

		super(File, self).save(*args, **kwargs)

	def as_json(self):
		return {
			"id": self.id,
			"mime": self.mime,
			"owner": self.owner_profile.as_json(),
		}

class Message(models.Model):
	profile = models.ForeignKey("Profile", on_delete=models.SET_NULL, null=True)
	target_puddle = models.ForeignKey("Puddle", on_delete=models.SET_NULL, null=True)
	timestamp = models.DateTimeField(default=timezone.now)

	readed_by = models.ManyToManyField("Profile", related_name="readed_by")
	not_show_for = models.ManyToManyField("Profile", related_name="not_show_for", blank=True)
	text = models.TextField(blank=True)

	files = models.ManyToManyField(File, blank=True)
	forwarded_messages = models.ManyToManyField("Message", blank=True)

	edited = models.BooleanField(default=False)

	def __str__(self):
		return f"{self.__class__.__name__}({self.id})"

	def save(self, *args, **kwargs):
		super(Message, self).save(*args, **kwargs)
		self.target_puddle.messages.add(self)

	def as_json(self):
		return {
			"id": self.id,
			"from": self.profile.user.username,
			"to_puddle_id": self.target_puddle.id,
			"timestamp": round(datetime.datetime.combine(self.timestamp.date(), self.timestamp.time()).replace(tzinfo=datetime.timezone.utc).astimezone(tz=None).timestamp()),
			"text": str(self.text),
			"readed_by": [i.user.username for i in self.readed_by.all()],
			"not_show_for": [i.user.username for i in self.not_show_for.all()],
			"files": [i.as_json() for i in self.files.all()],
			"forwarded_messages": [i.as_json() for i in self.forwarded_messages.all()],
			"edited": self.edited,
		}	

class Puddle(models.Model):
	creator = models.ForeignKey("Profile", related_name="puddle_creator", on_delete=models.SET_NULL, null=True)
	members = models.ManyToManyField("Profile")
	messages = models.ManyToManyField(Message, blank=True)
	not_show_for = models.ManyToManyField("Profile", related_name="not_show_puddle_for", blank=True)

	display_name = models.CharField(max_length=128, blank=True)
	avatar = models.ForeignKey(File, on_delete=models.SET_NULL, null=True, blank=True)

	@property
	def is_dialog(self):
		return self.members.count() <= 2

	def __str__(self):
		return f"{self.__class__.__name__}({self.id})"

	@property
	def name(self):
		return self.display_name or ", ".join([str(p.name) for p in self.members.all()[0:10]])

	@property
	def last_message(self):
		try:
			last_message = self.messages.all().last()
		except Message.DoesNotExist:
			return None
		else:
			return last_message

	def as_json(self):
		return {
			"id": self.id,
			"display_name": str(self.display_name),
			"avatar": self.avatar.id if self.avatar else None,
			"members": [i.user.username for i in self.members.all()],
			"not_show_for": [i.user.username for i in self.not_show_for.all()],
			"last_message": self.last_message.as_json() if self.messages.count() else None,
		}

class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True)
	puddles = models.ManyToManyField(Puddle, blank=True)
	friends = models.ManyToManyField("self", blank=True)

	display_name = models.CharField(max_length=128, blank=True)
	avatar = models.ForeignKey(File, on_delete=models.SET_NULL, null=True, blank=True)

	last_activity = models.DateTimeField(default=timezone.now)

	def __str__(self):
		return f"{self.__class__.__name__}({self.user})"

	@property
	def mutually_friends(self):
		mutually_friends_ids = []
		for friend in self.friends.all():
			if friend.friends.filter(id=self.id):
				mutually_friends_ids.append(friend.id)

		return Profile.objects.filter(id__in=mutually_friends_ids).exclude(id=self.id)

	@property
	def pretty_status(self):
		if self.is_online:
			return "Online"

		last_activity = datetime.datetime.combine(
			self.last_activity.date(),
			self.last_activity.time(),
			datetime.timezone.utc).replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)
		now = timezone.now()

		diff = (now-last_activity)

		if (not diff.days) and (diff.seconds//60 < 59):
			return f"Seen {diff.seconds//60} minute{'s' if diff.seconds//60 != 1 else ''} ago"
		elif (not diff.days):
			return f"Seen {diff.seconds//60//60} hour{'s' if diff.seconds//60//60 != 1 else ''} ago"
		elif 1 <= diff.days < 2:
			return last_activity.strftime("Seen yesterday at %H:%M")
		elif 2 <= diff.days < 7:
			return last_activity.strftime("Seen on %a at %H:%M")
		else:
			return last_activity.strftime("Seen on %d %b (%Y) at %H:%M")
	
	@property
	def name(self):
		return self.display_name or self.user.username

	@property
	def is_online(self):
		return (self.last_activity + datetime.timedelta(minutes=5)) >= timezone.now()

	@property
	def unreaded_messages(self):
		return Message.objects.filter(target_puddle__in=self.puddles.all()).exclude(readed_by=self).order_by("-timestamp")

	def as_json(self):
		return {
			"username": str(self.user.username),
			"friends": [i.user.username for i in self.friends.all().exclude(id=self.id)],
			"mutually_friends": [i.user.username for i in self.mutually_friends],
			"display_name": str(self.display_name),
			"avatar": self.avatar.id if self.avatar else None,
			"last_activity": round(datetime.datetime.combine(self.last_activity.date(), self.last_activity.time()).replace(tzinfo=datetime.timezone.utc).astimezone(tz=None).timestamp()),
		}