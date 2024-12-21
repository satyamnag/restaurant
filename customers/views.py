from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from app_accounts.views import check_role_customer
from app_accounts.forms import UserProfileForm, UserInfoForm
from app_accounts.models import UserProfile
from django.contrib import messages
from orders.models import Order, OrderedFood
import simplejson as json

# Create your views here.

@user_passes_test(check_role_customer)
def cprofile(request):
    profile=get_object_or_404(UserProfile, user=request.user)
    if request.method=='POST':
        profile_form=UserProfileForm(request.POST, request.FILES, instance=profile)
        user_form=UserInfoForm(request.POST, instance=request.user)
        if profile_form.is_valid() and user_form.is_valid():
            profile_form.save()
            user_form.save()
            messages.success(request, 'Profile updated')
            return redirect('cprofile')
        else:
            print(profile_form.errors)
            print(user_form.errors)
    else:
        profile_form=UserProfileForm(instance=profile)
        user_form=UserInfoForm(instance=request.user)

    context={
        'profile_form':profile_form,
        'user_form':user_form,
        'profile':profile,
    }
    return render(request, 'customers/cprofile.html', context)

def my_orders(request):
    orders=Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    context={
        'orders':orders,
    }
    return render(request, 'customers/my_orders.html', context)


def order_details(request, order_number):
    try:
        order=Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_food=OrderedFood.objects.filter(order=order)
        subtotal=0
        for food in ordered_food:
            subtotal+=(food.price*food.quantity)
        tax_data=json.loads(order.tax_data)
        context={
            'order':order,
            'ordered_food':ordered_food,
            'subtotal':subtotal,
            'tax_data':tax_data,
        }
        return render(request, 'customers/order_details.html', context)
    except:
        return redirect('customer')