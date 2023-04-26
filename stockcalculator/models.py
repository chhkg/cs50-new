import uuid
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.views.generic import ListView
from django.db import models
from django.contrib import admin

from .choices import ASSETS, FIATS, TYPES, FIATTYPES

class SoftDeleteModelManager(models.Manager):
    def all(self, include_deleted=False):
        if include_deleted:
            return self.get_queryset().all()
        return self.get_queryset().filter(deleted_at__isnull=True)
    def count(self, include_deleted=False):
        return self.all(include_deleted=include_deleted).count()
    def filter(self, *args, include_deleted=False, **kwargs):
        return self.all(
            include_deleted=include_deleted
        ).filter(*args, **kwargs)

class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.is_admin = True
        user.save()
        return user

class User(AbstractUser):
    username = None
    # id = models.UUIDField(primary_key=True, max_length=32, default=uuid.uuid4().hex, editable=False)
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True,)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    
    def has_perm(self, perm, obj=None):
        "The user has a specific permission?"
        return True

    def has_module_perms(self, app_label):
        "The user has permissions to view the app `app_label`?"
        return True
    
    @property
    def is_staff(self):
        # All admins are staff
        return self.is_admin
    

class Transaction(models.Model):
    # id = models.UUIDField(primary_key=True, max_length=32, default=uuid.uuid4().hex, editable=False)
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="transaction_user")
    asset = models.CharField(max_length=9, choices=ASSETS)
    date = models.DateField()
    currency = models.CharField(max_length=3, choices=FIATS, blank=True)
    type = models.CharField(max_length=10, choices=TYPES)
    symbol = models.CharField(max_length=50)
    quantity = models.DecimalField(max_digits=60, decimal_places=30, blank=True, null=True)
    price = models.DecimalField(max_digits=60, decimal_places=30, blank=True, null=True, default=None)
    proceed = models.DecimalField(max_digits=60, decimal_places=30, blank=True, null=True)
    fee = models.DecimalField(max_digits=60, decimal_places=30, blank=True, null=True)
    basis = models.DecimalField(max_digits=60, decimal_places=30)
    plpercent = models.DecimalField(max_digits=60, decimal_places=30, blank=True, null=True)
    pl = models.DecimalField(max_digits=60, decimal_places=30, blank=True, null=True)
    remark = models.TextField(max_length=500, blank=True)
    relatedbuytransaction = models.ManyToManyField("self", blank=True, symmetrical=False)
    relatedstockholdings = models.JSONField(blank=True, null=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    lastupdate = models.DateTimeField(auto_now=True)

    objects = SoftDeleteModelManager()

    def serialize(self):
        return {
            "id": self.id,
            "userid": self.user.id,
            "date": self.date,
            "currency": self.currency,
            "type": self.type,
            "symbol": self.symbol,
            "quantity": self.quantity,
            "price": self.price,
            "proceed": self.proceed,
            "fee": self.fee,
            "basis": self.basis,
            "plpercent": self.plpercent,
            "pl": self.pl,
            "remark": self.remark,
            "relatedbuytransaction": [transaction.id for transaction in self.relatedbuytransaction.all()],
            "relatedstockholdings": [self.relatedstockholdings],
            "deleted_at": self.deleted_at,
            "timestamp": self.timestamp,
            "lastupdate": self.lastupdate,
        }
    

    def related_buytransaction(self):
        return ",".join([str(transaction.id) for transaction in self.relatedbuytransaction.all()])
    
class TransactionAdmin(admin.ModelAdmin):
    list_display = ["id", "userid", "date", "asset", "type", "currency", "symbol", "quantity", "price", "proceed", "fee", "basis", 
                    "plpercent", "pl", "remark", "related_buytransaction", "relatedstockholdings", "deleted_at", "timestamp", "lastupdate"]
    ordering = ["-lastupdate"]
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs
    
    def userid(self, obj):
        return obj.user.id




class StockHolding(models.Model):
    # id = models.UUIDField(primary_key=True, max_length=32, default=uuid.uuid4().hex, editable=False)
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="stockholding_user")
    buytransaction = models.ForeignKey("Transaction", on_delete=models.CASCADE, related_name="stockholding_buytransaction")
    selltransaction = models.ManyToManyField("Transaction", blank=True, related_name="stockholding_selltransaction")
    buydate = models.DateField()
    currency = models.CharField(max_length=3, choices=FIATS, blank=True)
    symbol = models.CharField(max_length=50)
    original_quantity = models.DecimalField(max_digits=60, decimal_places=30) 
    quantity = models.DecimalField(max_digits=60, decimal_places=30)
    price = models.DecimalField(max_digits=60, decimal_places=30)
    deleted_at = models.DateTimeField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    lastupdate = models.DateTimeField(auto_now=True)

    objects = SoftDeleteModelManager()

    def serialize(self):
        return {
            "id": self.id,
            "userid": self.user.id,
            "buytransaction": self.buytransaction.id,
            "selltransaction": [transaction.id for transaction in self.selltransaction.all()],
            "buydate": self.buydate,
            "currency": self.currency,
            "symbol": self.symbol,
            "original_quantity": self.original_quantity,
            "quantity": self.quantity,
            "price": self.price,
            "deleted_at": self.deleted_at,
            "timestamp": self.timestamp,
            "lastupdate": self.lastupdate,
        }
    
    def sell_transaction(self):
        return ",".join([str(transaction.id) for transaction in self.selltransaction.all()])

class StockHoldingAdmin(admin.ModelAdmin):
    list_display = ["id", "userid", "buytransaction", "sell_transaction", "buydate", "currency", "symbol", "original_quantity", "quantity", "price", 
                    "deleted_at", "timestamp", "lastupdate"]
    ordering = ["-lastupdate"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs
    
    def userid(self, obj):
        return obj.user.id




class FiatHolding(models.Model):
    # id = models.UUIDField(primary_key=True, max_length=32, default=uuid.uuid4().hex, editable=False)
    relatedtransaction = models.ForeignKey("Transaction", on_delete=models.CASCADE, related_name="fiatholding_relatedtransaction")
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="fiatholding_user")
    date = models.DateField()
    currency = models.CharField(max_length=3, choices=FIATS, blank=True)
    amount = models.DecimalField(max_digits=60, decimal_places=30)
    type = models.CharField(max_length=10, choices=FIATTYPES)
    deleted_at = models.DateTimeField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    lastupdate = models.DateTimeField(auto_now=True)

    objects = SoftDeleteModelManager()

    def serialize(self):
        return {
            "id": self.id,
            "userid": self.user.id,
            "relatedtransaction": self.relatedtransaction.id, 
            "date": self.date,
            "currency": self.currency,
            "amount": self.amount,
            "type": self.type,
            "deleted_at": self.deleted_at,
            "timestamp": self.timestamp,
            "lastupdate": self.lastupdate,
        }
    
class FiatHoldingAdmin(admin.ModelAdmin):
    list_display = ["id", "userid", "relatedtransaction", "date", "currency", "amount", "type", "deleted_at", "timestamp", "lastupdate"]
    ordering = ["-lastupdate"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs
    
    def userid(self, obj):
        return obj.user.id
    


class CryptoHolding(models.Model):
    # id = models.UUIDField(primary_key=True, max_length=32, default=uuid.uuid4().hex, editable=False)
    relatedtransaction = models.ForeignKey("Transaction", on_delete=models.CASCADE, related_name="cryptoholding_relatedtransaction")
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="cryptoholding_user")
    date = models.DateField()
    currency = models.CharField(max_length=10)
    amount = models.DecimalField(max_digits=60, decimal_places=30)
    type = models.CharField(max_length=10, choices=TYPES)
    deleted_at = models.DateTimeField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    lastupdate = models.DateTimeField(auto_now=True)

    objects = SoftDeleteModelManager()

    def serialize(self):
        return {
            "id": self.id,
            "userid": self.user.id,
            "relatedtransaction": self.relatedtransaction.id, 
            "date": self.date,
            "currency": self.currency,
            "amount": self.amount,
            "type": self.type,
            "deleted_at": self.deleted_at,
            "timestamp": self.timestamp,
            "lastupdate": self.lastupdate,
        }
    
class CryptoHoldingAdmin(admin.ModelAdmin):
    list_display = ["id", "userid", "relatedtransaction", "date", "currency", "amount", "type", "deleted_at", "timestamp", "lastupdate"]
    ordering = ["-lastupdate"]

    
    def userid(self, obj):
        return obj.user.id