from django.urls import path, include
from .views import *
from django.contrib.auth import views as auth_views
from app_accounts import views as app_accounts_views

urlpatterns=[
    path('', app_accounts_views.restaurant_dashboard, name='vendor'),
    path('profile/', restaurant_profile, name='restaurant_profile'),
]