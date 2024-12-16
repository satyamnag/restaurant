from django.urls import path, include
from .views import *
from django.contrib.auth import views as auth_views

urlpatterns=[
    path('', myAccount),
    path('registerUser/', registerUser, name='registerUser'),
    path('registerRestaurant/', registerRestaurant, name='registerRestaurant'),
    path('login/', login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name="app_accounts/logout.html"), name="logout"),
    path('myAccount', myAccount, name='myAccount'),
    path('customer_dashboard/', customer_dashboard, name='customerDashboard'),
    path('restaurant_dashboard/', restaurant_dashboard, name='vendorDashboard'),
    path('activate/<uidb64>/<token>/', activate, name='activate'),
    path('forgot_password/', forgot_password, name='forgot_password'),
    path('reset_password_validate/<uidb64>/<token>/', reset_password_validate, name='reset_password_validate'),
    path('reset_password/', reset_password, name='reset_password'),
    path('vendor/', include('vendor.urls')),
    path('customer/', include('customers.urls')),
]