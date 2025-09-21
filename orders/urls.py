# orders/urls.py
from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    path("", views.order_view, name="order"),
    path("verify/", views.verify_code, name="verify"),
    path("resend/", views.resend_code, name="resend"),
    path("success/<int:order_id>/", views.order_success, name="success"),
    
]
# # orders/urls.py
# from django.urls import path
# from . import views

# app_name = "orders"

# # orders/urls.py
# urlpatterns = [
#     path("", views.order_view, name="order"),
#     path("verify/", views.verify_code, name="verify"),
#     path("resend/", views.resend_code, name="resend"),
#     path("success/<int:order_id>/", views.order_success, name="success"),
#     path("verify-code/", views.verify_code, name="verify_code"),
# ]

