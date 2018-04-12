from django.db import models

class Token(models.Model):
	profile = models.ForeignKey("web_mess.Profile", on_delete=models.CASCADE)
	token = models.CharField(max_length=256, db_index=True)