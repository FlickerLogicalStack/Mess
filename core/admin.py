from django.contrib import admin

from .models import File, Message, Puddle, Profile


admin.site.register(File)
admin.site.register(Message)
admin.site.register(Puddle)
admin.site.register(Profile)