from django.forms import *
from .models import *

class VendorForm(ModelForm):
    vendor_name=CharField(widget=TextInput(attrs={'placeholder': 'Enter your restaurant name'}))
    class Meta:
        model=Vendor
        fields=['vendor_name', 'vendor_license']