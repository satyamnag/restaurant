from django.urls import path
from app_accounts import views as AccountViews
from . import views

urlpatterns=[
    path('', AccountViews.customer_dashboard, name='customer'),
    path('profile/', views.cprofile, name='cprofile'),
]