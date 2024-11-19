from django.shortcuts import *
from .forms import *
from .models import *
from django.contrib import messages
from vendor.forms import *

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
            messages.success(request, 'Your account has been registered successfully!')
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
            messages.success(request, 'Your account has been registered successfully! Please wait for the approval.')
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