from django.forms import *
from .models import *

class UserForm(ModelForm):
    password=CharField(widget=PasswordInput())
    confirm_password=CharField(widget=PasswordInput())
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