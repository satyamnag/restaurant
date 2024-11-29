from django import forms
from .models import Category

class CategoryForm(forms.ModelForm):
    class Meta:
        model=Category
        fields=['category_name', 'description']
        widgets = {
            'category_name': forms.TextInput(attrs={'placeholder': 'Enter category name'}),
            'description': forms.Textarea(attrs={'placeholder': 'Enter description for the category'}),
        }