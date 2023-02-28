from django.contrib.auth.models import AbstractUser
from django.views.generic import ListView
from django.db import models
from django.contrib import admin
#from rest_framework import serializers

class User(AbstractUser):
    pass

"""class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']"""
""
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'email', 'date_joined', 'is_active', 'is_superuser']


class Post(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="posts_author")
    body = models.TextField()
    likes = models.ManyToManyField("User", blank=True, related_name="likes")
    timestamp = models.DateTimeField(auto_now_add=True)

    def serialize(self):
        return {
            "id": self.id,
            "userid": self.user.id,
            "username": self.user.username,
            "body": self.body,
            "likes": [user.id for user in self.likes.all()],
            "timestamp": self.timestamp.strftime("%b %d %Y, %I:%M %p"),
        }

    def liked_user(self):
        return ",".join([str(user.id) for user in self.likes.all()])

class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'body', 'liked_user', 'timestamp']


class Follow(models.Model):
    follower = models.ForeignKey("User", on_delete=models.CASCADE)
    following = models.ManyToManyField("User", related_name="following", blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def serialize(self):
        return {
            "id": self.id,
            "follower": self.user.username,
            "following": self.user.username,
            "timestamp": self.timestamp.strftime("%b %d %Y, %I:%M %p"),
        }
    

    def get_following(self):
        return "\n".join([f.username for f in self.following.all()])

class FollowAdmin(admin.ModelAdmin):
    list_display = ['id', 'follower', 'get_following', 'timestamp']