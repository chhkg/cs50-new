import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import HttpResponse, HttpResponseRedirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .models import User, Post, Follow


def index(request):
    # Return posts in reverse chronologial order
    posts = Post.objects.all().order_by("-timestamp").all()
    posts_paginator = Paginator(posts, 10)
    posts_page_number = request.GET.get('page')
    posts_page_obj = posts_paginator.get_page(posts_page_number)

    return render(request, "network/index.html", {
            "posts": posts,
            "posts_page_obj": posts_page_obj,
        })

@login_required
def following(request):
    # Return posts in reverse chronologial order
    
    try:
        follow = Follow.objects.get(follower=request.user)
    except Follow.DoesNotExist:
        posts = []
        posts_page_obj = []
        return render(request, "network/following.html", {
            "posts": posts,
            "posts_page_obj": posts_page_obj,
        })

    followlist = follow.following.all()
    posts = Post.objects.filter(user__in = followlist).order_by("-timestamp").all()
    posts_paginator = Paginator(posts, 10)
    posts_page_number = request.GET.get('page')
    posts_page_obj = posts_paginator.get_page(posts_page_number)

    return render(request, "network/following.html", {
            "posts": posts,
            "posts_page_obj": posts_page_obj,
        })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"].lower()
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

# Get posts of a user
@csrf_exempt
def postlist_user(request, user_id):

    # Check if the user id exists
    try:
        posts = Post.objects.filter(user__id=user_id).order_by("-timestamp").all()
        paginator = Paginator(posts, 10)

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return JsonResponse([post.serialize() for post in posts], safe=False)
    except Post.DoesNotExist:
        return JsonResponse({"error": "User not found."}, status=404)
    

def showfollowing(self):
    #followings = Follow.objects.filter(follower = request.user)
    followings = Follow.objects.all()
    return JsonResponse([following for following in followings], safe=False)

def profile(request, user_id):

    if not request.user.is_authenticated:
        return render(request, "network/login.html")

    else:
        try:
            username = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found."}, status=404)
        
        posts = Post.objects.filter(user__id=user_id).order_by("-timestamp").all()
        posts_paginator = Paginator(posts, 10)
        posts_page_number = request.GET.get('page')
        posts_page_obj = posts_paginator.get_page(posts_page_number)

        post_count = Post.objects.filter(user__id=user_id).count()
        follower_count = Follow.objects.filter(following__in=[user_id]).count()
        following_count = Follow.objects.filter(follower__id=user_id)
        if not following_count:
            following_count = 0
        else:
            following_count = following_count[0].following.count()
        
        following = Follow.objects.filter(follower=request.user)
        if following and username in following[0].following.all():
            following = True
        else:
            following = False

        return render(request, "network/profile.html", {
            "user_id": user_id,
            "username": username,
            "posts": posts,
            "posts_page_obj": posts_page_obj,
            "post_count": post_count,
            "follower_count": follower_count,
            "following_count": following_count,
            "following": following,
        })


@login_required
def newpost(request):

    if request.method == "POST":
        post = Post()
        post.user = request.user
        post.body = request.POST["newpost_body"]
        post.save()

        return HttpResponseRedirect(reverse("index"))
    else:
        return JsonResponse({"error": "POST request required."}, status=400)


@csrf_exempt
def post(request, post_id):

    # Query for requested post
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)

    # Return post contents
    if request.method == "GET":
        return JsonResponse({
            "post": post.serialize(),
            "authorid": post.user.id,
            "logged_in_user_id": request.user.id,
        })
    
    # Update the post body
    elif request.method == "PUT":
        if post.user.id == request.user.id:
            data = json.loads(request.body)
            post.body = data["body"]
            post.save()
            return HttpResponse(status=204)
        else:
            return JsonResponse({"error": "Not allowed to update this post."}, status=400)
    
    # Post must be via GET or PUT
    else:
        return JsonResponse({"error": "GET or PUT request required."}, status=400)

"""
@csrf_exempt
def edit_post(request, post_id):
    if request.method == "POST":
        post = Post.objects.get(id=post_id)
        post.body = request.POST["edit_body"]
        post.save()

        return render(request, "network/profile.html")
    else:
        return JsonResponse({"error": "POST request required."}, status=400)
"""

@login_required
@csrf_exempt
def like_post(request, post_id):
    # Query for requested post
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)

    # Unlike a post if the post is liked already
    if request.user in post.likes.all():
        post.likes.remove(request.user)
    # Like a post if it is not liked yet
    else:
        post.likes.add(request.user)

    return JsonResponse({"success": "Post like updated"})


@login_required
@csrf_exempt
def follow(request, following_user_id):
    #Query for requested following
    try:
        following = User.objects.get(pk=following_user_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found."}, status=404)

    # Create an object and follow the user if the request user did not follow anyone before
    try:
        follow = Follow.objects.get(follower=request.user)
    except Follow.DoesNotExist:
        follow = Follow()
        follow.follower = request.user
        follow.save()
        follow.following.add(following)
        return JsonResponse({"success": "Follow updated"})

    # Uollow the user
    if following in follow.following.all():
        follow.following.remove(following)
    
    # Follow the user
    else:
        follow.following.add(following)
    
    return JsonResponse({"success": "Follow updated"})
