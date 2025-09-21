# core/middleware.py
from django.shortcuts import redirect

class SaveLastVisitedMiddleware:
    """
    Save last requested page before login, so user gets redirected back.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated and request.path not in ["/login/", "/signup/"]:
            if request.method == "GET" and not request.path.startswith("/admin/"):
                request.session["prev_page"] = request.get_full_path()
        return self.get_response(request)