from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    bio = models.CharField(max_length=200, default='This user does not have any bio yet')
    user = models.OneToOneField(User, default=None, on_delete=models.PROTECT, related_name='profile_user')
    following = models.ManyToManyField(User, default=None, related_name='following')
    picture = models.FileField(blank=True)
    content_type = models.CharField(max_length=50)

    def __str__(self):
        return self.bio

class Room(models.Model):
    capacity = models.IntegerField(default=None),
    player = models.ManyToManyField(User, default=None)
    ready = models.BooleanField(default=False)

    def clean(self):
        cleaned_data = super().clean()
        capacity = cleaned_data.get('capacity')
        if capacity != 3 or capacity != 5:
            raise ValueError("Room number has to be either three or five.")
        return cleaned_data