from django.contrib import admin

from .models import File, Message, Puddle, Profile

class FileAdmin(admin.ModelAdmin):
    list_display = (
        "owner",
        "file",
        "mime",
        "file_hash"
        )

class MessageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "sender",
        "target_puddle",
        "timestamp",
        "text",
        "show_files",
        "show_forwarded",
        "readed_by",
        "show_hidden_from",
        "edited"
        )

    def show_forwarded(self, obj):
        return "\n".join([str(fmessage.id) for fmessage in obj.forwarded.all()])
    
    def show_files(self, obj):
        return "\n".join([str(file.id) for file in obj.files.all()])

    def show_hidden_from(self, obj):
        return "\n".join([str(profile.user.username) for profile in obj.hidden_from.all()])

class PuddleAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "creator",
        "title",
        "avatar",
        "show_members",
        "show_messages")

    def show_messages(self, obj):
        return "\n".join([str(message.id) for message in obj.messages.all()])

    def show_members(self, obj):
        return "\n".join([str(member.user.username) for member in obj.profile_set.all()])

class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "show_friends",
        "show_friend_requests",
        "show_puddles",
        "fullname",
        "avatar",
        "bio",
        "last_activity",
        )

    def show_puddles(self, obj):
        return "\n".join([str(puddle.id) for puddle in obj.puddles.all()])

    def show_friends(self, obj):
        return "\n".join([str(user.user.username) for user in obj.friends.all()])

    def show_friend_requests(self, obj):
        return "\n".join([str(user.user.username) for user in obj.friend_requests.all()])

admin.site.register(File, FileAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(Puddle, PuddleAdmin)
admin.site.register(Profile, ProfileAdmin)