# cart/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from .models import Cart
from menu.models import Item
from django.utils import timezone

@login_required
def add_to_cart(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    cart_item, created = Cart.objects.get_or_create(user=request.user, item=item)
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({
            "success": True,
            "item_name": item.name,
            "message": f"✔️ {item.name} successfully added to your cart"
        })

    messages.success(request, f"✔️ {item.name} successfully added to your cart")
    return redirect("cart:cart")

@login_required
def remove_from_cart(request, item_id):
    cart_item = Cart.objects.filter(user=request.user, item_id=item_id).first()
    if cart_item:
        cart_item.delete()
    return redirect("cart:cart")

@login_required
def buy_item(request, item_id):
    cart_item = Cart.objects.filter(user=request.user, item_id=item_id).first()
    if not cart_item:
        messages.error(request, "Item not found in your cart.")
        return redirect("cart:cart")

    order_items = [{
        "id": cart_item.item.id,
        "name": cart_item.item.name,
        "price": float(cart_item.item.price),
        "quantity": cart_item.quantity,
        "total": float(cart_item.total_price()),
        "image": cart_item.item.image.url if cart_item.item.image else ""
    }]
    grand_total = order_items[0]["total"]

    request.session["pending_order"] = {
        "items": order_items,
        "grand_total": round(grand_total, 2),
        "created_at": timezone.now().timestamp()
    }
    request.session.modified = True
    return redirect("orders:order")

@login_required
def buy_all_items(request):
    cart_items = Cart.objects.filter(user=request.user)
    if not cart_items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect("cart:cart")

    order_items, grand_total = [], 0.0
    for cart_item in cart_items:
        order_items.append({
            "id": cart_item.item.id,
            "name": cart_item.item.name,
            "price": float(cart_item.item.price),
            "quantity": cart_item.quantity,
            "total": float(cart_item.total_price()),
            "image": cart_item.item.image.url if cart_item.item.image else ""
        })
        grand_total += float(cart_item.total_price())

    request.session["pending_order"] = {
        "items": order_items,
        "grand_total": round(grand_total, 2),
        "created_at": timezone.now().timestamp()
    }
    request.session.modified = True
    return redirect("orders:order")

@login_required
def increase_quantity(request, item_id):
    cart_item = Cart.objects.filter(user=request.user, item_id=item_id).first()
    if cart_item:
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, f"✔️ 1 more {cart_item.item.name} added to your cart")
    return redirect("cart:cart")

@login_required
def decrease_quantity(request, item_id):
    cart_item = Cart.objects.filter(user=request.user, item_id=item_id).first()
    if cart_item:
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
            messages.error(request, f"❌ 1 {cart_item.item.name} removed from your cart")
        else:
            item_name = cart_item.item.name
            cart_item.delete()
            messages.error(request, f"⚠️ {item_name} removed from your cart")
    return redirect("cart:cart")

@login_required
def view_cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    cart_data = [{
        "id": c.item.id,
        "name": c.item.name,
        "price": c.item.price,
        "image": c.item.image.url if c.item.image else None,
        "quantity": c.quantity,
        "total": c.total_price(),
        "category": c.item.category,
    } for c in cart_items]
    grand_total = sum(i["total"] for i in cart_data)
    return render(request, "cart/cart.html", {
        "cart_items": cart_data,
        "grand_total": grand_total
    })

