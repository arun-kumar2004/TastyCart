from django.urls import path
from . import views

app_name = "menu"

urlpatterns = [
    path("add/", views.add_item, name="add_item"),
    path("menu/", views.menu_list, name="menu_list"),
    path("order/<int:item_id>/", views.order_from_menu, name="order_from_menu"),

    # NEW
    path("edit/<int:item_id>/", views.edit_item, name="edit_item"),
    path("delete/<int:item_id>/", views.delete_item, name="delete_item"),
    path(
    "category/add/",
    views.add_category,
    name="add_category",
),

path(
    "category/update/",
    views.update_category,
    name="update_category",
),
path(
    "category/delete/",
    views.delete_category,
    name="delete_category",
),
path(
    "search/",
    views.search_items,
    name="search_items",
),
]