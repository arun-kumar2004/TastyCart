from django.shortcuts import redirect
from django.conf import settings
from django.urls import reverse

class StoreLastURLMiddleware:
    """
    If user is not authenticated and tries to access a @login_required view,
    save that URL so after login they can be redirected back.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            if request.path not in [reverse("auth:login"), reverse("auth:logout")]:
                if request.method == "GET":
                    request.session["next_url"] = request.get_full_path()
        return self.get_response(request)
