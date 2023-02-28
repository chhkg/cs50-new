from django.contrib import admin
from .models import User, Post, Follow, UserAdmin, PostAdmin, FollowAdmin

# Register your models here.


admin.site.register(User, UserAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Follow, FollowAdmin)

