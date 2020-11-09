from django.db import models

class PrivacyLevel(models.TextChoices):
        PRIVATE = 'private', 'Private'
        PROTECTED = 'protected', 'Protected'
        PUBLIC = 'public', 'Public'

# Add idea - title, text, username, create_time
class Idea(models.Model):
    title = models.TextField()
    text = models.TextField()
    username = models.TextField()
    create_time = models.DateTimeField()
    privacy = models.TextField(choices=PrivacyLevel.choices)
    def __str__(self):
        return self.title

# Follower - a one-sided relationship between two users
class Following(models.Model):
    follower = models.TextField()
    follows = models.TextField()
    pending = models.BooleanField(default=True)
    def __str__(self):
        return self.follower + ":" + self.follows