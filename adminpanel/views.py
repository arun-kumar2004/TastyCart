from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test

def is_superuser(user):
    return user.is_authenticated and user.is_superuser

@user_passes_test(is_superuser)
def dashboard(request):
    return render(request, "adminpanel/dashboard.html")