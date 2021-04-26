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
    capacity = models.IntegerField(default=3)
    ready = models.BooleanField(null=True, blank=True, default=False)
    timeEnd = models.DateTimeField(null=True, blank=True, default=None)
    playerTurn = models.IntegerField(null=True, blank=True, default=None)
    phase = models.CharField(max_length=100, null=None, blank=None, default='')
    game_end = models.BooleanField(null=True, blank=True, default=False)
    winner = models.CharField(max_length=200, null=True, blank=True, default=None)
    msg = models.CharField(max_length=200, null=True, blank=True, default=None)
    voteTime = models.DateTimeField(null=True, blank=True, default=None)

    def clean(self):
        cleaned_data = super().clean()
        capacity = cleaned_data.get('capacity')
        if capacity != 3 or capacity != 5:
            raise ValueError("Room number has to be either three or five.")
        return cleaned_data


class Player(models.Model):
    player = models.OneToOneField(User, default=None, on_delete=models.PROTECT)
    room = models.ForeignKey(Room, null=True, blank=True, default=None, on_delete=models.PROTECT, related_name="player")
    game_id = models.IntegerField(null=True, blank=True, default=None)
    word = models.CharField(max_length=50, null=True, blank=True, default=None)
    identity = models.CharField(max_length=50, null=True, blank=True, default=None)
    is_dead = models.BooleanField(null=True, blank=True, default=False)
    vote = models.IntegerField(null=True, blank=True, default=None)


class Message(models.Model):
    player = models.ForeignKey(Player, null=True, blank=True, default=None, on_delete=models.PROTECT, related_name="message")
    content = models.CharField(null=True, blank=True, max_length=1000, default=None)
    timestamp = models.DateTimeField(null=True, blank=True, default=None)
    room = models.ForeignKey(Room, null=True, blank=True, on_delete=models.PROTECT)

    def __str__(self):
        return self.content