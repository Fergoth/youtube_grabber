from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class KeyWord(models.Model):
    key_word = models.CharField(max_length=200, unique=True)
    last_clip_time = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.key_word


class YoutubeClip(models.Model):
    key_word = models.ForeignKey(KeyWord, on_delete=models.CASCADE)
    url = models.URLField(max_length=200)
    uploaded = models.DateTimeField()

    def __str__(self):
        return self.key_word.__str__() + " : " + self.url
