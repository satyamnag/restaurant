from django.urls import path
from . import views

urlpatterns=[
    path('', views.marketplace, name='marketplace'),
    path('<slug:vendor_slug>/', views.vendor_detail, name='vendor_detail'),

    # Add to Cart
    path('add_to_cart/<int:food_id>/', views.add_to_cart, name='add_to_cart'),
    # Remove from Cart
    path('remove_from_cart/<int:food_id>/', views.remove_from_cart, name='remove_from_cart'),
    # Delete Cart Item
    path('delete_cart/<int:cart_id>/', views.delete_cart, name='delete_cart'),
]