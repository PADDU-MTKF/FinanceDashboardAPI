
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home),
    path("api/", views.home),
    
    # path("api/user", views.UserAPI.as_view()),
    # path("api/login", views.LoginAPI.as_view()),
    # path("api/event", views.EventAPI.as_view()),
    # path("api/updateEvent", views.UpdateEvent.as_view()),
    
]