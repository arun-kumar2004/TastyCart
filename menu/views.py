# menu/views.py
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import ItemForm
from .models import Item

def is_superuser(user):
    return user.is_authenticated and user.is_superuser

# Admin-only add item page
@login_required
@user_passes_test(is_superuser)
def add_item(request):
    """
    Admin-only view to add/edit menu items.
    Admin can check 'popular' to make item appear on home popular sections.
    """
    if request.method == "POST":
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.created_by = request.user
            item.save()
            messages.success(request, f"Item '{item.name}' saved successfully.")
            return redirect("menu:add_item")
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = ItemForm()
    return render(request, "menu/add_item.html", {"form": form})

# # Public menu list (all items)
# def menu_list(request):
#     items = Item.objects.all()
#     dishes = items.filter(category="Dish")
#     sweets = items.filter(category="Sweet")
#     return render(request, "menu/menu_list.html", {"items": items, "dishes": dishes, "sweets": sweets})

# menu/views.py
from cart.models import Cart   # ✅ add this import

def menu_list(request):
    items = Item.objects.all()
    dishes = items.filter(category="Dish")
    sweets = items.filter(category="Sweet")

    cart_item_ids = []
    if request.user.is_authenticated:
        cart_item_ids = list(
            Cart.objects.filter(user=request.user).values_list("item_id", flat=True)
        )

    return render(request, "menu/menu_list.html", {
        "items": items,
        "dishes": dishes,
        "sweets": sweets,
        "cart_item_ids": cart_item_ids,   # ✅ pass to template
    })

# optional: expose popular items for homepage use
def get_popular_items(limit=6):
    return Item.objects.filter(popular=True).order_by("-updated_at")[:limit]


@login_required
def order_from_menu(request, item_id):
    item = get_object_or_404(Item, id=item_id)

    order_items = [{
        "id": item.id,
        "name": item.name,
        "price": float(item.price),
        "quantity": 1,  # default 1
        "total": float(item.price),
        "image": item.image.url if item.image else ""
    }]
    grand_total = order_items[0]["total"]

    request.session["pending_order"] = {
        "items": order_items,
        "grand_total": round(grand_total, 2),
        "created_at": timezone.now().timestamp()
    }
    request.session.modified = True

    return redirect("orders:order")  # ⚡ same existing order_view


