from django.contrib import admin
from django.utils import timezone

from .models import File, Message, Puddle, Profile

class FileAdmin(admin.ModelAdmin):
	list_display = ("id", "file")

class MessageAdmin(admin.ModelAdmin):
	list_display = ("id", "profile", "target_puddle", "timestamp", "text", "show_forwarded")

	def show_forwarded(self, obj):
		return " ".join([str(fmessage.id) for fmessage in obj.forwarded_messages.all()])

class PuddleAdmin(admin.ModelAdmin):
	list_display = ("id", "show_members", "show_messages")

	def show_messages(self, obj):
		return " ".join([str(message.id) for message in obj.messages.all()])

	def show_members(self, obj):
		return " ".join([str(member.id) for member in obj.members.all()])



def make_selected_online(modeladmin, request, queryset):
	queryset.update(last_activity=timezone.now())

class ProfileAdmin(admin.ModelAdmin):
	list_display = ("id", "show_puddles", "user", "last_activity")
	actions = [make_selected_online]

	def show_puddles(self, obj):
		return " ".join([str(puddle.id) for puddle in obj.puddles.all()])


admin.site.register(File, FileAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(Puddle, PuddleAdmin)
admin.site.register(Profile, ProfileAdmin)