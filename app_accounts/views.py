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

def check_role_vendor(user):
    if user.role==1:
        return True
    else:
        raise PermissionDenied
    
def check_role_customer(user):
    if user.role==2:
        return True
    else:
        raise PermissionDenied

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

            return redirect('registerUser')
        else:
            form.errors
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
            user_profile=UserProfile.objects.get(user=user)
            vendor.user_profile=user_profile
            vendor.save()
            mail_subject='Restaurant: Please activate your account.'
            email_template='app_accounts/emails/account_verification_email.html'
            send_verification_email(request, user, mail_subject, email_template)

            return redirect('registerRestaurant')
        else:
            form.errors

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
            user=auth.authenticate(request, email=email, password=password)
            if user is not None:
                auth.login(request, user)
                return redirect('home')
            else:
                return redirect('login')
    return render(request, 'app_accounts/login.html')

def myAccount(request):
    user=request.user
    redirectUrl=detectUser(user)
    if redirectUrl is None:
        return redirect('login')
    if isinstance(redirectUrl, HttpResponseRedirect):
        return redirect(redirectUrl.url)
    return redirect(redirectUrl)

@user_passes_test(check_role_vendor)
def restaurant_dashboard(request):
    return render(request, 'app_accounts/restaurant_dashboard.html')

@user_passes_test(check_role_customer)
def customer_dashboard(request):
    return render(request, 'app_accounts/customer_dashboard.html')

def activate(request, uidb64, token):
    try:
        uid=urlsafe_base64_decode(uidb64).decode()
        user=User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user=None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active=True
        user.save()
        pass
    else:
        pass
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
                messages.success(request, 'A password reset link has been sent to your email.')
                return redirect('forgot_password')
            else:
                messages.error(request, 'No account found with this email address.')
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
        messages.info(request, 'Please reset your password!')
        return redirect('reset_password')
    else:
        messages.error(request, 'This link has been expired')
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
            messages.success(request, 'Password reset successfully!')
            return redirect('login')
        else:
            messages.error(request, 'Password do not match.')
            return redirect('reset_password')
    return render(request, 'app_accounts/reset_password.html')