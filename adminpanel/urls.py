from django.urls import path
from . import views

app_name = "adminpanel"

urlpatterns = [

    # ==========================================================
    # Dashboard
    # ==========================================================

    path(
        "",
        views.dashboard,
        name="dashboard"
    ),

]