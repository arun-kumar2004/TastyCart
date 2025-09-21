# yourproject/middleware.py
class PreviousURLMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        # store only if it's not AJAX
        if "HTTP_REFERER" in request.META:
            request.session["back_url"] = request.META.get("HTTP_REFERER")
        return response
