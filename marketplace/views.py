from django.shortcuts import render, get_object_or_404, redirect
from vendor.models import Vendor
from menu.models import Category, FoodItem
from django.db.models import Prefetch
from django.http import HttpResponse, JsonResponse
from .models import Cart
from .context_processors import get_cart_count, get_cart_amounts
from app_accounts.views import check_role_customer, check_role_vendor
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from vendor.models import OpeningHour
from datetime import date
import datetime as dt
from orders.forms import OrderForm
from app_accounts.models import UserProfile

# Create your views here.
def marketplace(request):
    vendors=Vendor.objects.filter(is_approved=True,user__is_active=True)
    vendor_count=vendors.count()

    context={
        'vendors':vendors,
        'vendor_count':vendor_count,
    }
    return render(request, 'marketplace/listings.html', context)

def vendor_detail(request, vendor_slug):
    vendor=get_object_or_404(Vendor, vendor_slug=vendor_slug)
    categories=Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch(
            'fooditems',
            queryset=FoodItem.objects.filter(is_available=True)
        )
    )

    opening_hours=OpeningHour.objects.filter(vendor=vendor).order_by('day', '-from_hour')

    # today opening hours
    today_date=date.today()
    today=today_date.isoweekday()
    today_opening_hours=OpeningHour.objects.filter(vendor=vendor, day=today)
    
    if request.user.is_authenticated:
        cart_items=Cart.objects.filter(user=request.user)
    else:
        cart_items = Cart.objects.none()

    context={
        'vendor':vendor,
        'categories':categories,
        'cart_items':cart_items,
        'opening_hours':opening_hours,
        'today_opening_hours':today_opening_hours,
    }
    return render(request, 'marketplace/vendor_detail.html', context)


def add_to_cart(request, food_id):
    if request.user.is_authenticated:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Check if the food item exists
            try:
                fooditem=FoodItem.objects.get(id=food_id)
                # Check if the user has already added the food to the cart
                try:
                    chkCart=Cart.objects.get(user=request.user, fooditem=fooditem)
                    # Increate the cart quantity for the food
                    chkCart.quantity+=1
                    chkCart.save()
                    return JsonResponse({'status':'success', 'message': 'increased the cart quantity of the food', 'cart_counter':get_cart_count(request), 'qty':chkCart.quantity, 'cart_amount':get_cart_amounts(request)})
                except:
                    chkCart=Cart.objects.create(user=request.user, fooditem=fooditem, quantity=1)
                    return JsonResponse({'status':'success', 'message':'added the food to the cart', 'cart_counter':get_cart_count(request), 'qty':chkCart.quantity, 'cart_amount':get_cart_amounts(request)})
            except:
                return JsonResponse({'status':'failed', 'message':'this food does not exist'})
        else:
            return JsonResponse({'status':'failed', 'message':'invalid request'})
    else:
        return JsonResponse({'status':'login_required', 'message':'please login to continue'})

def remove_from_cart(request, food_id):
    if request.user.is_authenticated:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Check if the food item exists
            try:
                fooditem=FoodItem.objects.get(id=food_id)
                # Check if the user has already added the food to the cart
                try:
                    chkCart=Cart.objects.get(user=request.user, fooditem=fooditem)
                    if chkCart.quantity>1:
                    # Decrease the cart quantity for the food
                        chkCart.quantity-=1
                        chkCart.save()
                    else:
                        chkCart.delete()
                        chkCart.quantity=0
                    return JsonResponse({'status':'success', 'cart_counter':get_cart_count(request), 'qty':chkCart.quantity, 'cart_amount':get_cart_amounts(request)})
                except:
                    return JsonResponse({'status':'failed', 'message':'you do not have this food item in your cart'})
            except:
                return JsonResponse({'status':'failed', 'message':'this food does not exists'})
        else:
            return JsonResponse({'status':'failed', 'message':'invalid request'})
    else:
        return JsonResponse({'status':'login_required', 'message':'please login to continue'})
    
@user_passes_test(check_role_customer)
def cart(request):
    cart_items=Cart.objects.filter(user=request.user).order_by('created_at')
    context={
        'cart_items':cart_items,
    }
    return render(request, 'marketplace/cart.html', context)

def delete_cart(request, cart_id):
    if request.user.is_authenticated:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                # check if the cart item exists
                cart_item=Cart.objects.get(user=request.user, id=cart_id)
                if cart_item:
                    cart_item.delete()
                    return JsonResponse({'status':'success', 'message':'cart item has been deleted successfully!', 'cart_counter':get_cart_count(request), 'cart_amount':get_cart_amounts(request)})
            except:
                return JsonResponse({'status':'failed', 'message':'this cart item does not exists'})
        else:
            return JsonResponse({'status':'failed', 'message':'invalid request'})
        

def search(request):
    if not 'address' in request.GET:
        return redirect('marketplace')
    else:
        keyword=request.GET['keyword']
        address=request.GET['address']
        latitude=request.GET['lat']
        longitude=request.GET['lng']
        radius=request.GET['radius']

        # get vendor ids that has the food item the user is looking for
        fetch_vendors_by_fooditems=FoodItem.objects.filter(food_title__icontains=keyword, is_available=True).values_list('vendor', flat=True)
        
        vendors=Vendor.objects.filter(Q(id__in=fetch_vendors_by_fooditems) | Q(vendor_name__icontains=keyword, is_approved=True, user__is_active=True))
        if latitude and longitude and radius:
            pnt = GEOSGeometry('POINT(%s %s)' % (longitude, latitude))
            vendors=Vendor.objects.filter(Q(id__in=fetch_vendors_by_fooditems) | Q(vendor_name__icontains=keyword, is_approved=True, user__is_active=True), user_profile__location__distance_lte=(pnt, D(km=radius))).annotate(distance=Distance('user_profile__location', pnt)).order_by('distance')
            for vendor in vendors:
                vendor.kms=round(vendor.distance.km, 1)
        vendor_count=vendors.count()
        context={
            'vendors':vendors,
            'vendor_count':vendor_count,
            'source_location':address,
        }
        return render(request, 'marketplace/listings.html', context)
    
@user_passes_test(check_role_customer)
def checkout(request):
    cart_items=Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count=cart_items.count()
    if cart_count<=0:
        return redirect('marketplace')
    user_profile=UserProfile.objects.get(user=request.user)
    default_values={
        'first_name':request.user.first_name,
        'last_name':request.user.last_name,
        'phone':request.user.phone_number,
        'email':request.user.email,
        'address':user_profile.address,
        'country':user_profile.country,
        'state':user_profile.state,
        'city':user_profile.city,
        'pin_code':user_profile.pin_code,
    }
    form=OrderForm(initial=default_values)
    context={
        'form':form,
        'cart_items':cart_items,
    }
    return render(request, 'marketplace/checkout.html', context)