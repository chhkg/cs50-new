from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, redirect
from django.urls import reverse

from .models import User, Listing, Bid, Comment


def index(request):
    item = Listing.objects.filter(listing_status = True).order_by('-posting_date')

    return render(request, "auctions/index.html", {
        "item": item
    })

@login_required(login_url='login')
def watchlist(request):
    item = User.objects.get(id=request.user.id).watchlist.all()

    return render(request, "auctions/watchlist.html", {
        "item": item
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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required(login_url='login')
def createlisting(request):
    poster = request.user

    if request.method =="POST":
        user = poster
        listing_name = request.POST["listingtitle"]
        listing_desc = request.POST["listingdescription"]
        starting_bid = request.POST["startbid"]
        
        image = request.POST["listingimage"]
        if not image:
            image = "https://nayemdevs.com/wp-content/uploads/2020/03/default-product-image.png"
        category = request.POST["listingcategory"].title()
        if not category:
            category = "No Category"

        newlisting = Listing(user=user,listing_name=listing_name,listing_desc=listing_desc,starting_bid=starting_bid,image=image,category=category)
        newlisting.save()

        return redirect('listing', listing_id=newlisting.id)
    else:
        return render(request, "auctions/createlisting.html", {
            "poster": poster,
        })


def listing(request, listing_id):
    try:
        listing = Listing.objects.get(id=listing_id)
    except Listing.DoesNotExist:
        return redirect('/')
    
    comment = Comment.objects.filter(listing=listing_id).order_by('-comment_time')
    user = request.user
    
    try:
        watchlist_item = User.objects.get(id=request.user.id).watchlist.all()    
    except User.DoesNotExist:
        watchlist_item = None

    try:
        bid = Bid.objects.filter(listing=listing_id).latest('bid_time')
        bid_count = Bid.objects.filter(listing=listing_id).count()
    except Bid.DoesNotExist:
        bid = None
        bid_count = None
    
    if request.method == "POST":
        # Close bid by listing owner
        if 'close_bid' in request.POST:
            
            listing.listing_status = "False"
            listing.save()

            # Decide the winner if there is a bid
            if bid is not None and bid.user:
                bid.bid_win = "True"
                bid.save()

            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        #New comment by user
        elif 'submit_comment' in request.POST:
            
            new_comment_content = request.POST["comment"]
            new_comment = Comment(user=request.user, listing=listing, comment=new_comment_content)
            new_comment.save()

            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        #Remove listing from watchlist
        elif 'remove_watchlist' in request.POST:
            listing.watchlist.remove(user)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        #Add listing to watchlist
        elif 'add_watchlist' in request.POST:
            listing.watchlist.add(user)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        #If user click add watchlist without loggin in
        elif 'go_to_login' in request.POST:
            return HttpResponseRedirect(reverse("login"))

        #If user place a bid
        elif 'new_bid' in request.POST:
            user_bid = float(request.POST["new_bid"])

            #Bid is successful if user's bid is more than the latest bid or the starting bid
            if (user_bid > listing.current_bid and listing.current_bid != 0.00) or (user_bid >= listing.starting_bid and listing.current_bid == 0.00):

                listing.current_bid = user_bid
                listing.save()

                new_bid_insert = Bid(user=request.user, listing=listing, bid=user_bid)
                new_bid_insert.save()

                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            
            
            #Alert the user if the bid is too low
            else:  
                return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "comment": comment,
                    "bid": bid,
                    "watchlist_item":watchlist_item,
                    "bid_count": bid_count,
                    "message": "Your bid is too low"
                })
        else:
            return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "comment": comment,
                    "bid": bid,
                    "watchlist_item":watchlist_item,
                    "bid_count": bid_count,
                    "message": "System Error"
                })

    else:
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "comment": comment,
            "bid": bid,
            "watchlist_item":watchlist_item,
            "bid_count": bid_count,
        })


def categorylist(request):
    category = Listing.objects.filter(listing_status=True).values("category").annotate(Count("id"))

    return render(request, "auctions/categorylist.html", {
        "category": category,
    })

def category(request, category):
    item = Listing.objects.filter(category__iexact=category, listing_status=True).order_by('-posting_date')

    return render(request, "auctions/category.html", {
        "category": category,
        "item": item
    })
