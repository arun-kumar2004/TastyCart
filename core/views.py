from django.shortcuts import render
from menu.models import Item
from cart.models import Cart

def home(request):
    # Select only popular items
    popular_items = Item.objects.filter(popular=True).exclude(name__isnull=True).exclude(name__exact='').order_by("-updated_at")
    
    # Separate into dishes and sweets
    popular_dishes = popular_items.filter(category="Dish")[:6]
    popular_sweets = popular_items.filter(category="Sweet")[:6]

    # Get cart item IDs safely
    if request.user.is_authenticated:
        cart_ids = Cart.objects.filter(user=request.user).values_list('item_id', flat=True)
    else:
        cart_ids = []  # Empty list for anonymous users

    context = {
        "dishes": popular_dishes,
        "sweets": popular_sweets,
        "cart_ids": list(cart_ids),
    }

    return render(request, "home.html", context)
