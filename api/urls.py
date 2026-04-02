
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home),
    path("api/", views.home),
    
    path("api/login", views.LoginAPI.as_view()),
    path("api/createUser", views.CreateUserAPI.as_view()),
    path("api/deleteUser", views.DeleteUserAPI.as_view()),
    path("api/updateUserRole", views.UpdateUserRoleAPI.as_view()),
    path("api/updateUserStatus", views.UpdateUserStatusAPI.as_view()),
    path("api/listUsers", views.ListUsersAPI.as_view()),
    # path("api/event", views.EventAPI.as_view()),
    # path("api/updateEvent", views.UpdateEvent.as_view()),
    
]