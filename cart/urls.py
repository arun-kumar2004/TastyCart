from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.view_cart, name='cart'),
    path('add/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('buy/<int:item_id>/', views.buy_item, name='buy_item'),
    path('buy-all/', views.buy_all_items, name='buy_all_items'),
    path("increase/<int:item_id>/", views.increase_quantity, name="increase_quantity"),
    path("decrease/<int:item_id>/", views.decrease_quantity, name="decrease_quantity"),
    
]
