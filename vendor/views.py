from django.shortcuts import render, get_object_or_404, redirect
from .forms import VendorForm
from app_accounts.forms import UserProfileForm
from app_accounts.models import UserProfile
from .models import Vendor
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from app_accounts.views import check_role_vendor

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