from django.forms import *
from .models import *
from .validators import allow_only_images_validator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class UserForm(ModelForm):
    first_name=CharField(widget=TextInput(attrs={'placeholder': 'Enter your first name'}))
    last_name=CharField(widget=TextInput(attrs={'placeholder': 'Enter your last name'}))
    email=CharField(widget=TextInput(attrs={'placeholder': 'Enter your email address'}))
    username=CharField(widget=TextInput(attrs={'placeholder': 'Enter your username'}))
    password=CharField(widget=PasswordInput(attrs={'placeholder': 'Enter your password'}))
    confirm_password=CharField(widget=PasswordInput(attrs={'placeholder': 'Confirm your password'}))

    class Meta:
        model=User
        fields=['first_name', 'last_name', 'username', 'email', 'password']

    def clean(self):
        cleaned_data=super(UserForm, self).clean()
        password=cleaned_data.get('password')
        confirm_password=cleaned_data.get('confirm_password')

        if password!=confirm_password:
            raise ValidationError(
                "The passwords do not match."
            )
        
# @login_required
class UserProfileForm(ModelForm):
    address=CharField(widget=TextInput(attrs={'placeholder': 'Start typing...'}))
    profile_picture=FileField(widget=FileInput(attrs={'class':'btn btn-info'}), validators=[allow_only_images_validator])
    cover_photo=FileField(widget=FileInput(attrs={'class':'btn btn-info'}), validators=[allow_only_images_validator])

    # latitude=CharField(widget=TextInput(attrs={'readonly':'readonly', 'style':'color:gray;'}))
    # longitude=CharField(widget=TextInput(attrs={'readonly':'readonly', 'style':'color:gray;'}))
    class Meta:
        model=UserProfile
        fields=['profile_picture', 'cover_photo', 'address', 'country', 'state', 'city', 'pin_code', 'latitude', 'longitude']

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            if field=='latitude' or field=='longitude':
                widget = self.fields[field].widget
                if isinstance(widget.attrs, dict):
                    widget.attrs['readonly'] = 'readonly'
                    widget.attrs['style'] = 'color: gray;'
