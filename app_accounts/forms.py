from django.forms import *
from .models import *

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