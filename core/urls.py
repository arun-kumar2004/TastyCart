from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path(
        "mindset/",
        views.developer_page,
        name="developer_page"
    ),
    
]
