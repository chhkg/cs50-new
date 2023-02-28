
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("following", views.following, name="following"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("profile/<int:user_id>", views.profile, name="profile"),

    # API Routes
    path("newpost", views.newpost, name="newpost"),
    path("user/post/<int:user_id>", views.postlist_user, name="userpost"),
    path("post/<int:post_id>", views.post, name="post"),
    path("postlike/<int:post_id>", views.like_post, name="like_post"),
    path("follow/<int:following_user_id>", views.follow, name="follow"),
]
