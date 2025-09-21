from django.urls import path
from . import views

 

urlpatterns = [
    path('login/', views.login_view, name="login"),
    path('signup/', views.signup_view, name="signup"),
    path('ajax-login/', views.ajax_login, name="ajax_login"),
    path('logout/', views.logout_view, name="logout"),
    path('update-profile/', views.update_profile, name="update_profile"),

    # Password reset
    path('password-reset/', views.password_reset, name='password_reset'),
    path('password-reset/done/', views.password_reset_done, name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('password-reset-complete/', views.password_reset_complete, name='password_reset_complete'),
]
