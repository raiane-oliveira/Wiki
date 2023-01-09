from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:titleEntry>", views.wiki, name="wiki"),
    path("newpage", views.createPage, name="newPage"),
    path("randomPage", views.randomPage, name="randomPage"),
    path("wiki/<str:titleEntry>/editPage", views.editPage, name="editPage"),
    path("search", views.search, name="search")
]
