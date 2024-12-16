from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from app_accounts.views import check_role_customer, check_role_vendor
from app_accounts.forms import UserProfileForm, UserInfoForm
from app_accounts.models import UserProfile, User
from django.contrib import messages

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