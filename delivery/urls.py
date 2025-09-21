from django.urls import path
from . import views

app_name = "delivery"

urlpatterns = [
    path("", views.delivery_view, name="delivery"),
    path("send-otp/<int:order_id>/", views.send_delivery_otp, name="send_delivery_otp"),
    path("verify-otp/<int:order_id>/", views.verify_delivery_otp, name="verify_delivery_otp"),
    path("delete/<int:order_id>/", views.delete_order, name="delete_order"),
    path("update-status/<int:order_id>/", views.update_order_status, name="update_order_status"),
    path("send-cancel-otp/<int:order_id>/", views.send_cancel_otp, name="send_cancel_otp"),
    path("verify-cancel-otp/<int:order_id>/", views.verify_cancel_otp, name="verify_cancel_otp"),
    

]



# # delivery/urls.py
# from django.urls import path
# from . import views

# app_name = "delivery"

# urlpatterns = [
#     path("", views.delivery_view, name="delivery"),

#     # Delivery OTP
#     # path("send-otp/<int:order_id>/", views.send_delivery_otp, name="send_delivery_otp"),
#     # path("verify-otp/<int:order_id>/", views.verify_delivery_otp, name="verify_delivery_otp"),
#     path("send-cancel-otp/<int:order_id>/", views.send_cancel_otp, name="send_cancel_otp"),
#     path("verify-cancel-otp/<int:order_id>/", views.verify_cancel_otp, name="verify_cancel_otp"),

#     # Update status (admin only)
#     path("update-status/<int:order_id>/", views.update_order_status, name="update_order_status"),

#     # Delete (admin only)
#     path("delete/<int:order_id>/", views.delete_order, name="delete_order"),
# ]

# # delivery/urls.py
# from django.urls import path
# from . import views

# app_name = "delivery"

# urlpatterns = [
#     path("", views.delivery_view, name="delivery"),
#     path("send-otp/<int:order_id>/", views.send_delivery_otp, name="send_delivery_otp"),
#     path("verify-otp/<int:order_id>/", views.verify_delivery_otp, name="verify_delivery_otp"),
# ]