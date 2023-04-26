from django.urls import path

from . import views
from .views import LoginView, RegisterView

urlpatterns = [
    path("", views.index, name="index"),
    path("currentholding", views.currentholding, name="currentholding"),
    path("transaction", views.transaction, name="transaction"),
    path("performance", views.performance, name="performance"),
    path("login", LoginView.as_view(), name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", RegisterView.as_view(), name="register"),
    
    #API
    # path("createtransaction", views.createtransaction, name="createtransaction"),
    path("edittransaction/<int:transaction_id>", views.edit_transaction, name="edit_transaction"),
    path("deletetransaction/<int:transaction_id>", views.delete_transaction, name="delete_transaction"),
    
]