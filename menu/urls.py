# menu/urls.py
from django.urls import path
from . import views

app_name = "menu"

urlpatterns = [
    path("", views.menu_list, name="menu_list"),     # url: /menu/
    path("add/", views.add_item, name="add_item"),   # url: /menu/add/
    path("order/menu/<int:item_id>/", views.order_from_menu, name="order_from_menu"),
]
