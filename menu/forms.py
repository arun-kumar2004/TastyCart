# menu/forms.py
from django import forms
from .models import Item, Category


class ItemForm(forms.ModelForm):

    class Meta:

        model = Item

        fields = [
            "name",
            "description",
            "price",
            "category",
            "image",
            "popular",
        ]

        widgets = {

            "name": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "Item Name"
            }),

            "description": forms.Textarea(attrs={
                "class": "form-textarea",
                "rows": 3
            }),

            "price": forms.NumberInput(attrs={
                "class": "form-input",
                "step": "0.01"
            }),

            "category": forms.Select(attrs={
                "class": "form-control",
                "id": "id_category"
            }),

            "popular": forms.CheckboxInput(attrs={
                "class": "form-checkbox"
            }),

        }


class CategoryForm(forms.ModelForm):

    class Meta:

        model = Category

        fields = ["name"]

        widgets = {

            "name": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "Enter Category Name"
            })

        }