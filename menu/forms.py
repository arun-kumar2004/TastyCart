# menu/forms.py
from django import forms
from .models import Item

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ["name", "description", "price", "category", "image", "popular"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-input", "placeholder": "Item name"}),
            "description": forms.Textarea(attrs={"class": "form-textarea", "rows": 3, "placeholder": "Short description"}),
            "price": forms.NumberInput(attrs={"class": "form-input", "step": "0.01"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "popular": forms.CheckboxInput(attrs={"class": "form-checkbox"}),
        }
