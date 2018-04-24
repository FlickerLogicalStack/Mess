import time

from django.apps import apps
from django.contrib.auth.models import User

from rest_framework import serializers

Profile = apps.get_model("core", "Profile")
Puddle = apps.get_model("core", "Puddle")
Message = apps.get_model("core", "Message")
File = apps.get_model("core", "File")

class FileSerializer(serializers.ModelSerializer):
	link = serializers.SerializerMethodField()

	class Meta:
		model = File
		fields = (
			"id",
			"mime",
			"link",
			"file_hash"
			)

	def get_link(self, obj):
		return obj.file.url

class MessageSerializer(serializers.ModelSerializer):
	sender = serializers.SerializerMethodField()
	forwarded = serializers.SerializerMethodField()
	timestamp = serializers.SerializerMethodField()
	files = FileSerializer(many=True)
	
	class Meta:
		model = Message
		fields = (
			"id",
			"sender",
			"target_puddle",
			"timestamp",
			"text",
			"files",
			"forwarded",
			"edited",
			)

	def get_sender(self, obj):
		return obj.sender.user.username

	def get_forwarded(self, obj):
		return [ForwardedMessageSerializer(fmessage).data for fmessage in obj.forwarded.all()]

	def get_timestamp(self, obj):
		return time.mktime(obj.timestamp.timetuple())+25200

class ForwardedMessageSerializer(serializers.ModelSerializer):
	files = FileSerializer(many=True)
	timestamp = serializers.SerializerMethodField()

	class Meta:
		model = Message
		fields = (
			"id",
			"sender",
			"timestamp",
			"text",
			"files",
			"edited"
			)

	def get_timestamp(self, obj):
		return time.mktime(obj.timestamp.timetuple())

class PuddleSerializer(serializers.ModelSerializer):
	creator = serializers.SerializerMethodField()
	users = serializers.SerializerMethodField()
	title = serializers.SerializerMethodField()
	messages_count = serializers.SerializerMethodField()
	last_message = serializers.SerializerMethodField()

	class Meta:
		model = Puddle
		fields = (
			"id",
			"creator",
			"users",
			"messages_count",
			"title",
			"avatar",
			"last_message",
			)

	def get_creator(self, obj):
		return ProfileSerializer(obj.creator).data

	def get_users(self, obj):
		return [profile.user.username for profile in obj.users.all()]

	def get_messages_count(self, obj):
		return obj.messages.all().count()

	def get_title(self, obj) :
		return obj.title or ", ".join([(profile.fullname or profile.user.username) for profile in obj.users.all()])

	def get_last_message(self, obj):
		if obj.last_message:
			return MessageSerializer(obj.last_message).data
		else:
			return None

class ProfileSerializer(serializers.ModelSerializer):
	username = serializers.SerializerMethodField()
	last_activity = serializers.SerializerMethodField()
	friends = serializers.SerializerMethodField()
	avatar = FileSerializer()

	class Meta:
		model = Profile
		fields = (
			"id",
			"username",
			"fullname",
			"avatar",
			"bio",
			"last_activity",
			"friends",
			)

	def to_representation(self, obj):
		representation = super(ProfileSerializer, self).to_representation(obj)

		if not representation["fullname"]:
			representation.pop("fullname")
		return representation

	def get_friends(self, obj):
		return [profile.user.username for profile in obj.friends.all() if obj.user.username != profile.user.username]

	def get_username(self, obj):
		return obj.user.username

	def get_last_activity(self, obj):
		return time.mktime(obj.last_activity.timetuple())+25200

class SelfProfileSerializer(ProfileSerializer):
	friend_requests = serializers.SerializerMethodField()

	class Meta:
		model = Profile
		fields = (
			"id",
			"username",
			"fullname",
			"avatar",
			"bio",
			"last_activity",
			"friends",
			"friend_requests",
			"puddles",
			)

	def get_friends(self, obj):
		return super().get_friends(obj)

	def get_friend_requests(self, obj):
		return [profile.user.username for profile in obj.friend_requests.all()]