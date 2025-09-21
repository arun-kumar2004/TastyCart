"""
URL configuration for TastyCart project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # App urls
    path('', include('core.urls')),        # Home & base pages
    path('users/', include('users.urls')), # Signup, login, profile
    path('menu/', include('menu.urls')),   # Food items
    path('contact/', include('contact.urls')),   # Food items
    path('cart/', include('cart.urls')),   # Add to cart
    path("order/", include("orders.urls", namespace="orders")),# Place orders
    path('accounts/', include("allauth.urls")),  # google login
    path("delivery/", include("delivery.urls", namespace="delivery")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)