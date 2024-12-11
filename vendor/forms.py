from django.forms import *
from .models import *
from app_accounts.validators import allow_only_images_validator

class VendorForm(ModelForm):
    vendor_name=CharField(widget=TextInput(attrs={'placeholder': 'Enter your restaurant name'}))
    vendor_license=FileField(widget=FileInput(attrs={'class':'btn btn-info w-100'}), validators=[allow_only_images_validator])
    class Meta:
        model=Vendor
        fields=['vendor_name', 'vendor_license']

class OpeningHourForm(ModelForm):
    class Meta:
        model=OpeningHour
        fields=['day', 'from_hour', 'to_hour', 'is_closed']