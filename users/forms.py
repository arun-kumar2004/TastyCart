
from django import forms
from django.contrib.auth.forms import UserCreationForm
from core.models import CustomUser

class SignupForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=True)
    address = forms.CharField(widget=forms.Textarea, required=True)
    profile_pic = forms.ImageField(required=False)  # New field for profile pic

    class Meta:
        model = CustomUser
        fields = ["first_name", "email", "phone", "address", "profile_pic", "password1", "password2"]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if CustomUser.objects.filter(phone=phone).exists():
            raise forms.ValidationError("This phone number is already registered.")
        return phone
