from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.forms import PasswordResetForm

from .forms import SignupForm
from core.models import CustomUser
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from core.models import CustomUser
from django.http import JsonResponse



from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages
from django.conf import settings
from django.urls import reverse

User = get_user_model()

def password_reset(request):
    if request.method == "POST":
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            # ✅ No namespace here
            reset_link = request.build_absolute_uri(
                reverse("password_reset_confirm", kwargs={"uidb64": uid, "token": token})
            )

            subject = "Password Reset Request"
            message = render_to_string('auth/registration/password_reset_email.html', {
                'user': user,
                'reset_link': reset_link
            })
            send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])
            return redirect('password_reset_done')

        except User.DoesNotExist:
            messages.error(request, "Email not found")
    return render(request, 'auth/registration/password_reset_form.html')


def password_reset_done(request):
    return render(request, 'auth/registration/password_reset_done.html')


def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user and default_token_generator.check_token(user, token):
        if request.method == "POST":
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            if password1 == password2:
                user.set_password(password1)
                user.save()
                return redirect('password_reset_complete')
            else:
                messages.error(request, "Passwords do not match")
        return render(request, 'auth/registration/password_reset_confirm.html', {'validlink': True})
    else:
        return render(request, 'auth/registration/password_reset_confirm.html', {'validlink': False})


def password_reset_complete(request):
    return render(request, 'auth/registration/password_reset_complete.html')
 



def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    # Store previous page URL before login
    if request.method == "GET":
        prev_url = request.META.get('HTTP_REFERER')
        if prev_url and prev_url != request.build_absolute_uri():
            request.session['prev_page'] = prev_url

    if request.method == "POST":
        login_input = request.POST.get("username")
        password = request.POST.get("password")
        user = None

        try:
            user_obj = CustomUser.objects.get(
                Q(username=login_input) | Q(email=login_input) | Q(phone=login_input)
            )
            user = authenticate(request, username=user_obj.username, password=password)
        except CustomUser.DoesNotExist:
            user = None

        if user:
            login(request, user)
            messages.success(request, f"✅ Welcome back {user.username}!")

            # Instead of redirect, render login page with JS back
            return render(request, "auth/login.html", {"login_success": True, "user_name": user.username})
        else:
            messages.error(request, "❌ Invalid credentials")

    return render(request, "auth/login.html")


@ensure_csrf_cookie
def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST, request.FILES)  # include request.FILES for profile pic
        if form.is_valid():
            user = form.save(commit=False)
            user.username = form.cleaned_data["email"]
            user.first_name = form.cleaned_data["first_name"]
            user.phone = form.cleaned_data["phone"]
            user.address = form.cleaned_data["address"]
            user.user_type = "customer"
            if form.cleaned_data.get('profile_pic'):
                user.profile_pic = form.cleaned_data['profile_pic']  # save uploaded pic
            user.save()

            if not hasattr(user, 'backend'):
                from django.conf import settings
                user.backend = settings.AUTHENTICATION_BACKENDS[0]

            login(request, user)

            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({
                    "success": True,
                    "name": user.first_name,
                    "redirect": "/"
                })
            else:
                messages.success(request, f"✅ {user.first_name} successfully signed up!")
                return redirect("home")
        else:
            errors = {k: [str(e) for e in v] for k, v in form.errors.items()}
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({
                    "success": False,
                    "form_errors": errors,
                    "error": "Form validation failed"
                })
            messages.error(request, "❌ Signup failed. Please correct the errors.")
    else:
        form = SignupForm()

    return render(request, "auth/signup.html", {"form": form})


def logout_view(request):
    if request.user.is_authenticated:
        name = request.user.username
        logout(request)
        messages.success(request, f"👋 {name} successfully logged out")
    return redirect("home")


 

def ajax_login(request):
    if request.method == "POST":
        login_input = request.POST.get("username")
        password = request.POST.get("password")
        user = None

        try:
            user_obj = CustomUser.objects.get(
                Q(username=login_input) | Q(email=login_input) | Q(phone=login_input)
            )
            user = authenticate(request, username=user_obj.username, password=password)
        except CustomUser.DoesNotExist:
            user = None

        if user:
            # Set backend if multiple backends exist
            if not hasattr(user, 'backend'):
                from django.conf import settings
                user.backend = settings.AUTHENTICATION_BACKENDS[0]
            login(request, user)
            return JsonResponse({"success": True, "user_name": user.username, "redirect_to": "/"})

        return JsonResponse({"success": False, "message": "Invalid credentials"})

    return JsonResponse({"success": False, "message": "Invalid request"})


@login_required
def update_profile(request):
    user = request.user

    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        first_name = request.POST.get("first_name")
        phone = request.POST.get("phoneNumber")
        address = request.POST.get("deliveryAddress")
        current_password = request.POST.get("currentPassword")
        profile_pic = request.FILES.get("profile_pic")  # ✅ must get file here

        if not current_password:
            return JsonResponse({"success": False, "message": "Please enter your current password to update profile."})

        if not user.check_password(current_password):
            return JsonResponse({"success": False, "message": "Incorrect password. Please try again."})

        if first_name:
            user.first_name = first_name
        if phone:
            user.phone = phone
        if address:
            user.address = address

        # Handle profile image update
        if profile_pic:
            if user.profile_pic and user.profile_pic.name:
                try:
                    user.profile_pic.delete(save=False)  # remove old image file
                except Exception:
                    pass
            user.profile_pic = profile_pic

        user.save()

        # Return new image URL to update preview dynamically
        new_image_url = user.profile_pic.url if user.profile_pic else ""

        return JsonResponse({
            "success": True,
            "message": f"✔️ {user.first_name or 'User'}, your details are updated successfully",
            "new_image_url": new_image_url  # ✅ key for JS to update preview
        })

    # GET request renders the profile page
    return render(request, "auth/update_profile.html", {"user": user})
