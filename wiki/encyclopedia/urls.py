from django.urls import path

from . import views

app_name = "encyclopedia"

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:title>", views.entry, name="entry"),
    path("newpage", views.newpage, name="newpage"),
    path("editpage", views.editpage, name="editpage"),
    path("randompage", views.randompage, name="randompage")
]
