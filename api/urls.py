
from django.contrib import admin
from django.urls import path
from . import views
from .views import docs_redirect


urlpatterns = [
    path("", views.home),
    path("api/", views.home),
    path('docs/', docs_redirect),
    
    path("api/login", views.LoginAPI.as_view()),
    path("api/createUser", views.CreateUserAPI.as_view()),
    path("api/deleteUser", views.DeleteUserAPI.as_view()),
    path("api/updateUserRole", views.UpdateUserRoleAPI.as_view()),
    path("api/updateUserStatus", views.UpdateUserStatusAPI.as_view()),
    path("api/listUsers", views.ListUsersAPI.as_view()),
    
    path("api/addTransaction", views.AddTransactionAPI.as_view()),
    path("api/updateTransaction", views.UpdateTransactionAPI.as_view()),
    path("api/deleteTransaction", views.DeleteTransactionAPI.as_view()),
    path("api/getTransactions", views.GetTransactionAPI.as_view()),
    
    path("api/getInsights", views.TransactionInsightsAPI.as_view()),

    
]