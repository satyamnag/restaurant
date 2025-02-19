from django.shortcuts import *
from .forms import *
from .models import *
from django.contrib import auth, messages
from vendor.forms import *
from django.contrib.auth import logout
from django.contrib.auth.decorators import user_passes_test
from .utils import *
from django.core.exceptions import PermissionDenied
from django.utils.http import urlsafe_base64_decode
from vendor.models import Vendor
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import AnonymousUser
from django.template.defaultfilters import slugify
from orders.models import Order
import datetime


def check_role_vendor(user):
    if isinstance(user, AnonymousUser):
        raise PermissionDenied("You must be logged in to access this resource.")
    elif user.role == 1:
        return True
    else:
        raise PermissionDenied("You do not have permission to access this resource.")
    

def check_role_customer(user):
    if isinstance(user, AnonymousUser):
        raise PermissionDenied("You must be logged in to access this resource.")
    elif user.role == 2:
        return True
    else:
        raise PermissionDenied("You do not have permission to access this resource.")
    

# Create your views here.
def registerUser(request):
    if request.method=='POST':
        form=UserForm(request.POST)
        if form.is_valid():
            
            # Create user using form
            # password=form.cleaned_data['password']
            # user=form.save(commit=False)
            # user.set_password(password)
            # user.role=User.CUSTOMER
            # user.save()
        
            # Create user using create_user method
            first_name=form.cleaned_data['first_name']
            last_name=form.cleaned_data['last_name']
            username=form.cleaned_data['username']
            email=form.cleaned_data['email']
            password=form.cleaned_data['password']
            user=User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password,
            )
            user.role=User.CUSTOMER
            user.save()
            mail_subject='Restaurant: Please activate your account.'
            email_template='app_accounts/emails/account_verification_email.html'
            send_verification_email(request, user, mail_subject, email_template)

            messages.success(request, 'Your account has been created successfully. Please check your email to verify your account.')

            return redirect('login')
        else:
            messages.error(request, 'There were some problems with your submission. Please check the form and try again.')
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form=UserForm()
    
    context={
        'form':form,
    }
    return render(request, 'app_accounts/registerUser.html', context)

def registerRestaurant(request):
    if request.method=='POST':
        form=UserForm(request.POST)
        vendor_form=VendorForm(request.POST, request.FILES)
        if form.is_valid() and vendor_form.is_valid():
            first_name=form.cleaned_data['first_name']
            last_name=form.cleaned_data['last_name']
            username=form.cleaned_data['username']
            email=form.cleaned_data['email']
            password=form.cleaned_data['password']
            user=User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password,
            )
            user.role=User.RESTAURANT
            user.save()
            vendor=vendor_form.save(commit=False)
            vendor.user=user
            vendor_name=vendor_form.cleaned_data['vendor_name']
            vendor.vendor_slug=slugify(vendor_name)+'-'+str(user.id)
            user_profile=UserProfile.objects.get(user=user)
            vendor.user_profile=user_profile
            vendor.save()
            mail_subject='Restaurant: Please activate your account.'
            email_template='app_accounts/emails/account_verification_email.html'
            send_verification_email(request, user, mail_subject, email_template)

            messages.success(request, 'Your restaurant account has been created successfully. Please check your email to activate your account.')

            return redirect('registerRestaurant')
        else:
            messages.error(request, 'There were errors with your submission. Please check the form and try again.')

            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            for field, errors in vendor_form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form=UserForm()
        vendor_form=VendorForm()
    context={
        'form':form,
        'vendor_form':vendor_form,
    }
    return render(request, 'app_accounts/registerRestaurant.html', context)


def login(request):
    if request.method=='POST':
        if 'password' in request.POST:
            email=request.POST['email']
            password=request.POST['password']
            if email and password:
                user=auth.authenticate(request, email=email, password=password)
                if user is not None:
                    auth.login(request, user)
                    messages.success(request, 'You have logged in successfully.')
                    return redirect('home')
                else:
                    messages.error(request, 'Invalid email or password. Please try again.')
                    return redirect('login')
            else:
                messages.error(request, 'Please enter both email and password.')
                return redirect('login')
    else:
        return render(request, 'app_accounts/login.html')


def myAccount(request):
    user=request.user
    redirectUrl=detectUser(user)
    if redirectUrl is None:
        messages.error(request, 'You need to log in to access this page.')
        return redirect('login')
    if isinstance(redirectUrl, HttpResponseRedirect):
        return redirect(redirectUrl.url)
    return redirect(redirectUrl)

@user_passes_test(check_role_vendor)
def restaurant_dashboard(request):
    vendor=Vendor.objects.get(user=request.user)
    orders=Order.objects.filter(vendors__in=[vendor.id], is_ordered=True).order_by('-created_at')
    recent_orders=orders[:100]

    # Current month's revenue
    current_month=datetime.datetime.now().month
    current_month_orders=orders.filter(vendors__in=[vendor.id], created_at__month=current_month)

    current_month_revenue=0
    for current_month_order in current_month_orders:
        current_month_revenue+=current_month_order.get_total_by_vendor()['grand_total']

    # Total revenue
    total_revenue=0
    for order in orders:
        total_revenue += order.get_total_by_vendor()['grand_total']

    context={
        'orders':orders,
        'orders_count':orders.count(),
        'recent_orders':recent_orders,
        'total_revenue':total_revenue,
        'current_month_revenue':current_month_revenue,
    }
    return render(request, 'app_accounts/restaurant_dashboard.html', context)

@user_passes_test(check_role_customer)
def customer_dashboard(request):
    orders=Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    recent_orders=orders[:100]
    context={
        'orders':orders,
        'orders_count':orders.count(),
        'recent_orders':recent_orders,
    }
    return render(request, 'app_accounts/customer_dashboard.html', context)

def activate(request, uidb64, token):
    try:
        uid=urlsafe_base64_decode(uidb64).decode()
        user=User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user=None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active=True
        user.save()
        messages.success(request, 'Your account has been activated successfully. You can now log in.')
    else:
        messages.error(request, 'The activation link is invalid or expired.')
    return redirect('myAccount')

def forgot_password(request):
    if request.method=='POST':
        if 'email' in request.POST:
            email=request.POST['email']
            if User.objects.filter(email=email).exists():
                user=User.objects.get(email__exact=email)

                mail_subject='Restaurant: Please reset you password.'
                email_template='app_accounts/emails/reset_password_email.html'
                send_verification_email(request, user, mail_subject, email_template)
                messages.success(request, 'A password reset link has been sent to your email address.')
                return redirect('forgot_password')
            else:
                messages.error(request, 'No account found with this email address. Please check and try again.')
                return redirect('forgot_password')
    return render(request, 'app_accounts/forgot_password.html')

def reset_password_validate(request, uidb64, token):
    try:
        uid=urlsafe_base64_decode(uidb64).decode()
        user=User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user=None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] =uid
        messages.info(request, 'Please reset your password.')
        return redirect('reset_password')
    else:
        messages.error(request, 'This link has expired or is invalid.')
        return redirect('myAccount')


def reset_password(request):
    if request.method=='POST':
        password=request.POST['password']
        confirm_password=request.POST['confirm_password']

        if password == confirm_password:
            pk=request.session.get('uid')
            user=User.objects.get(pk=pk)
            user.set_password(password)
            user.is_active=True
            user.save()
            messages.success(request, 'Your password has been reset successfully. You can now log in with your new password.')
            return redirect('login')
        else:
            messages.error(request, 'Passwords do not match. Please try again.')
            return redirect('reset_password')
    return render(request, 'app_accounts/reset_password.html')