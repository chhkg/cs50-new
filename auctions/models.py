from django.contrib.auth.models import AbstractUser
from django.db import models
from decimal import Decimal


class User(AbstractUser):
    pass

class Listing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='poster')
    listing_name = models.CharField(max_length=50)
    listing_desc = models.CharField(max_length=500)
    listing_status = models.BooleanField(default=True)
    starting_bid = models.DecimalField(decimal_places=2, max_digits=10, default=Decimal('0.00'))
    current_bid = models.DecimalField(decimal_places=2, max_digits=10, default=Decimal('0.00'))
    image = models.URLField(max_length=250, default='https://nayemdevs.com/wp-content/uploads/2020/03/default-product-image.png')
    category = models.CharField(max_length=30, default='No Category')
    posting_date = models.DateTimeField(auto_now_add=True)
    watchlist = models.ManyToManyField(User, blank=True, related_name='watchlist')

    
    def __str__(self):
        return f"{self.listing_name} ({self.id})"
    
    
class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    bid = models.DecimalField(decimal_places=2, max_digits=10, default=Decimal('0.00'))
    bid_win = models.BooleanField(default=False)
    bid_time = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.listing.listing_name} ({self.listing.id}) ${self.bid}"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    comment = models.CharField(max_length=5000)
    comment_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.listing.listing_name} ({self.listing.id}) {self.comment}"