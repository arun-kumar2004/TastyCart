from django.utils.deprecation import MiddlewareMixin

def back_url(request):
    return {
        "back_url": request.META.get("HTTP_REFERER", "/")
    }
