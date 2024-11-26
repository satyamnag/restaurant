from django.forms import *
from .models import *
from app_accounts.validators import allow_only_images_validator

class VendorForm(ModelForm):
    vendor_name=CharField(widget=TextInput(attrs={'placeholder': 'Enter your restaurant name'}))
    vendor_license=FileField(widget=FileInput(attrs={'class':'btn btn-info'}), validators=[allow_only_images_validator])
    class Meta:
        model=Vendor
        fields=['vendor_name', 'vendor_license']