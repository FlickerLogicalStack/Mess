from django.contrib import admin

from .models import Token

class TokenAdmin(admin.ModelAdmin):
	list_display = ("id", "profile", "token")

admin.site.register(Token, TokenAdmin)