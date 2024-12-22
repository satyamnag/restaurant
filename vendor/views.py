from django.shortcuts import render, get_object_or_404, redirect

from orders.models import Order, OrderedFood
from .forms import VendorForm, OpeningHourForm
from app_accounts.forms import UserProfileForm
from app_accounts.models import UserProfile
from .models import Vendor, OpeningHour
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from app_accounts.views import check_role_vendor
from menu.models import Category
from menu.models import FoodItem
from menu.forms import CategoryForm, FoodItemForm
from django.template.defaultfilters import slugify
from django.http import HttpResponse
from django.db import IntegrityError
from django.http import JsonResponse


def get_vendor(request):
    vendor=Vendor.objects.get(user=request.user)
    return vendor

# Create your views here.
@user_passes_test(check_role_vendor)
def restaurant_profile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    vendor = get_object_or_404(Vendor, user=request.user)

    # If the request is POST, process the form submissions
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        vendor_form = VendorForm(request.POST, request.FILES, instance=vendor)
        
        # Check if both forms are valid
        if profile_form.is_valid() and vendor_form.is_valid():
            profile_form.save()
            vendor_form.save()
            messages.success(request, "Settings updated!")
            return redirect('restaurant_profile')  # Redirect after successful POST
        
        else:
            # If forms are invalid, print errors for debugging
            print(profile_form.errors)
            print(vendor_form.errors)

    else:
        # If the request is GET, create empty forms pre-populated with user data
        profile_form = UserProfileForm(instance=profile)
        vendor_form = VendorForm(instance=vendor)

    # Prepare the context for rendering
    context = {
        'user_profile_form': profile_form,
        'vendor_profile_form': vendor_form,
        'profile': profile,
        'vendor': vendor,
    }

    # Always return a response (render the template)
    return render(request, 'vendor/restaurant_profile.html', context)

@user_passes_test(check_role_vendor)
def menu_builder(request):
    vendor=get_vendor(request)
    categories=Category.objects.filter(vendor=vendor).order_by('created_at')
    context={
        'categories':categories,
    }
    return render(request, 'vendor/menu_builder.html', context)

@user_passes_test(check_role_vendor)
def fooditems_by_category(request, pk=None):
    vendor=get_vendor(request)
    category=get_object_or_404(Category, pk=pk)
    fooditems=FoodItem.objects.filter(vendor=vendor, category=category)
    context={
        'fooditems':fooditems,
        'category':category,
    }
    return render(request, 'vendor/fooditems_by_category.html', context)

@user_passes_test(check_role_vendor)
def add_category(request):
    if request.method=='POST':
        form=CategoryForm(request.POST)
        if form.is_valid():
            category_name=form.cleaned_data['category_name']
            category=form.save(commit=False)
            category.vendor=get_vendor(request)
            category.save()
            category.slug=slugify(category_name)+'-'+str(category.id)
            category.save()
            messages.success(request, 'Category added successfully!')
            return redirect('menu_builder')
    else:
        form=CategoryForm()
    context={
        'form':form,
    }
    return render(request, 'vendor/add_category.html', context)

@user_passes_test(check_role_vendor)
def edit_category(request, pk=None):
    category=get_object_or_404(Category, pk=pk)
    if request.method=='POST':
        form=CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category_name=form.cleaned_data['category_name']
            category=form.save(commit=False)
            category.vendor=get_vendor(request)
            category.slug=slugify(category_name)
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('menu_builder')
    else:
        form=CategoryForm(instance=category)
    context={
        'form':form,
        'category':category,
    }
    return render(request, 'vendor/edit_category.html', context)

@user_passes_test(check_role_vendor)
def delete_category(request, pk=None):
    category=get_object_or_404(Category, pk=pk)
    category.delete()
    messages.info(request, 'Category has been deleted successfully!')
    return redirect('menu_builder')

@user_passes_test(check_role_vendor)
def add_food(request):
    if request.method=='POST':
        form=FoodItemForm(request.POST, request.FILES)
        if form.is_valid():
            food_title=form.cleaned_data['food_title']
            food=form.save(commit=False)
            food.vendor=get_vendor(request)
            food.slug=slugify(food_title)
            form.save()
            messages.success(request, 'Food Item added successfully!')
            return redirect('fooditems_by_category', food.category.id)
    else:
        form=FoodItemForm()
        form.fields['category'].queryset=Category.objects.filter(vendor=get_vendor(request))
    context={
        'form':form,
    }
    return render(request, 'vendor/add_food.html', context)

@user_passes_test(check_role_vendor)
def edit_food(request, pk=None):
    food=get_object_or_404(FoodItem, pk=pk)
    if request.method=='POST':
        form=FoodItemForm(request.POST, request.FILES, instance=food)
        if form.is_valid():
            food_title=form.cleaned_data['food_title']
            food=form.save(commit=False)
            food.vendor=get_vendor(request)
            food.slug=slugify(food_title)
            form.save()
            messages.success(request, 'Food Item updated successfully!')
            return redirect('fooditems_by_category', food.category.id)
    else:
        form=FoodItemForm(instance=food)
        form.fields['category'].queryset=Category.objects.filter(vendor=get_vendor(request))
    context={
        'form':form,
        'food':food,
    }
    return render(request, 'vendor/edit_food.html', context)

@user_passes_test(check_role_vendor)
def delete_food(request, pk=None):
    food=get_object_or_404(FoodItem, pk=pk)
    food.delete()
    messages.info(request, 'Food Item has been deleted successfully!')
    return redirect('fooditems_by_category', food.category.id)


def opening_hours(request):
    opening_hours=OpeningHour.objects.filter(vendor=get_vendor(request))
    form=OpeningHourForm()
    context={
        'form':form,
        'opening_hours':opening_hours,
    }
    return render(request, 'vendor/opening_hours.html', context)


def add_opening_hours(request):
    # handle the data and save them inside database
    if request.user.is_authenticated:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and request.method=='POST':
            day=request.POST.get('day')
            from_hour=request.POST.get('from_hour')
            to_hour=request.POST.get('to_hour')
            is_closed=request.POST.get('is_closed')

            existing_hour = OpeningHour.objects.filter(vendor=get_vendor(request), day=day).first()
            if existing_hour:
                if existing_hour:
                    if not existing_hour.is_closed:
                        return JsonResponse({
                            'status': 'failed', 
                            'message': f'{existing_hour.get_day_display()} already has opening hours set.'
                        })
                    else:
                        return JsonResponse({
                            'status': 'failed', 
                            'message': f'{existing_hour.get_day_display()} already has closing hours.'
                        })
                else:
                    existing_hour.delete()
            try:
                hour=OpeningHour.objects.create(
                    vendor=get_vendor(request),
                    day=day,
                    from_hour=from_hour,
                    to_hour=to_hour,
                    is_closed=is_closed
                    )
                if hour:
                    day=OpeningHour.objects.get(id=hour.id)
                    if day.is_closed:
                        response={'status':'success', "id":hour.id, 'day':day.get_day_display(), 'is_closed':'Closed'}
                    else:
                        response={'status':'success', "id":hour.id, 'day':day.get_day_display(), 'from_hour':hour.from_hour, 'to_hour':hour.to_hour}
                    return JsonResponse(response)
                response={'status':'success'}
                return JsonResponse(response)
            except IntegrityError as e:
                return JsonResponse({'status': 'failed', 'message': from_hour+'-'+to_hour+' already exists for the day!'})
            except Exception as e:
                return JsonResponse({'status': 'failed', 'message': str(e)})
        else:
            return JsonResponse({'status': 'failed', 'message': 'Invalid request type'})

    return JsonResponse({'status': 'failed', 'message': 'User not authenticated'})


def remove_opening_hours(request, pk=None):
    if request.user.is_authenticated:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            hour=get_object_or_404(OpeningHour, pk=pk)
            hour.delete()
            return JsonResponse({'status':'success', 'id':pk})
        

def order_details(request, order_number):
    try:
        order=Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_food=OrderedFood.objects.filter(order=order, fooditem__vendor=get_vendor(request))
        context={
            'order':order,
            'ordered_food':ordered_food,
            'subtotal':order.get_total_by_vendor()['subtotal'],
            'tax_data':order.get_total_by_vendor()['tax_dict'],
            'grand_total':order.get_total_by_vendor()['grand_total'],
        }
    except:
        return redirect('vendor')
    return render(request, 'vendor/order_details.html', context)

def my_orders(request):
    vendor=Vendor.objects.get(user=request.user)
    orders=Order.objects.filter(vendors__in=[vendor.id], is_ordered=True).order_by('-created_at')
    context={
        'orders':orders,
    }
    return render(request, 'vendor/my_orders.html', context)