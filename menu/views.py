# menu/views.py
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import ItemForm
from .models import Item, Category
from .forms import CategoryForm
from django.http import JsonResponse
from django.core.files.storage import default_storage
from cart.models import Cart   # ✅ add this import
from django.http import JsonResponse

from django.db.models import Prefetch
import os
import requests
from urllib.parse import urlparse
from django.core.files.base import ContentFile

def is_superuser(user):
    return user.is_authenticated and user.is_superuser

from django.http import JsonResponse

def search_items(request):

    keyword = request.GET.get("q","").strip()

    items = Item.objects.filter(
        name__icontains=keyword
    ).select_related("category")[:30]

    data = []

    for item in items:

        data.append({

            "id":item.id,
            "name":item.name,
            "category":item.category.id

        })

    return JsonResponse(data,safe=False)

# Admin-only add item page
@login_required
@user_passes_test(is_superuser)
def add_item(request):
    """
    Admin-only view to add/edit menu items.
    Supports:
    - Upload file
    - Image URL (downloads image and stores locally)
    """
    if request.method == "POST":

        form = ItemForm(request.POST, request.FILES)

        if form.is_valid():
            item = form.save(commit=False)
            item.created_by = request.user

            uploaded_image = request.FILES.get("image")

            # Prevent Django from saving original filename
            item.image = None

            item.save()

            uploaded_image = request.FILES.get("image")

            if uploaded_image:

                safe_name = "".join(
                    c if c.isalnum() else "_"
                    for c in (item.name or "tastycart")
                )

                ext = os.path.splitext(uploaded_image.name)[1].lower()

                if not ext:
                    ext = ".jpg"

                filename = f"{safe_name}_{item.id}{ext}"
                filepath = f"items/{filename}"

                if default_storage.exists(filepath):
                    default_storage.delete(filepath)

                item.image.save(
                    filename,
                    uploaded_image,
                    save=False
                )

            else:
                # Default placeholder image
                item.image.name = "items/item_placeholder.png"

            item.save()

            messages.success(
                request,
                f"Item '{item.name}' saved successfully."
            )

            return redirect("menu:add_item")

        else:
            messages.error(request, "Please fix the errors below.")

    else:
        form = ItemForm()

    return render(
    request,
    "menu/add_item.html",
    {
        "form": form,
        "categories": Category.objects.all().order_by("name"),
        "open_category_popup": request.GET.get("manage_category") == "1",
    },
)



def menu_list(request):

    categories = Category.objects.prefetch_related(
        Prefetch(
            "items",
            queryset=Item.objects.all().order_by("-created_at")
        )
    ).order_by("name")

    cart_item_ids = []

    if request.user.is_authenticated:
        cart_item_ids = list(
            Cart.objects.filter(user=request.user)
            .values_list("item_id", flat=True)
        )

    recommended_items = (
        Item.objects
        .filter(popular=True)      # Only items selected for Home
        .select_related("category")
        .order_by("?")             # Shuffle randomly
    )

    
    recommended_count = recommended_items.count()

    # Only split when more than 10 items
    if recommended_count > 10:
        split_index = (recommended_count + 1) // 2
    else:
        split_index = recommended_count

    return render(
        request,
        "menu/menu_list.html",
        {
            "categories": categories,
            "cart_item_ids": cart_item_ids,
            "recommended_items": recommended_items,
            "split_index": split_index,
            "recommended_count": recommended_count,
        },
    )

# optional: expose popular items for homepage use
def get_popular_items(limit=6):
    return Item.objects.filter(popular=True).order_by("-updated_at")[:limit]

@login_required
@user_passes_test(is_superuser)
def edit_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)

    if request.method == "POST":
        form = ItemForm(request.POST, request.FILES, instance=item)

        if form.is_valid():
            item = form.save(commit=False)

            uploaded_image = request.FILES.get("image")

            # -------------------------------
            # If a NEW image is uploaded
            # -------------------------------
            if uploaded_image:

                # Delete old image (if exists)
                if item.image and default_storage.exists(item.image.name):
                    default_storage.delete(item.image.name)

                # Safe filename
                safe_name = "".join(
                    c if c.isalnum() else "_"
                    for c in (item.name or "tastycart")
                )

                ext = os.path.splitext(uploaded_image.name)[1].lower()

                if not ext:
                    ext = ".jpg"

                filename = f"{safe_name}_{item.id}{ext}"

                # Save new image
                item.image.save(
                    filename,
                    uploaded_image,
                    save=False
                )

            # -------------------------------
            # If image NOT changed
            # -------------------------------
            elif item.image:

                safe_name = "".join(
                    c if c.isalnum() else "_"
                    for c in (item.name or "tastycart")
                )

                old_path = item.image.name
                ext = os.path.splitext(old_path)[1].lower()

                if not ext:
                    ext = ".jpg"

                filename = f"{safe_name}_{item.id}{ext}"
                new_path = f"items/{filename}"

                # Rename only if name changed
                if old_path != new_path and default_storage.exists(old_path):

                    with default_storage.open(old_path, "rb") as f:
                        item.image.save(
                            filename,
                            ContentFile(f.read()),
                            save=False
                        )

                    default_storage.delete(old_path)

            # Save all changes
            item.save()

            messages.success(request, "Item updated successfully.")
            return redirect("menu:menu_list")

        else:
            messages.error(request, "Please correct the errors below.")

    else:
        form = ItemForm(instance=item)

    return render(
        request,
        "menu/add_item.html",
        {
            "form": form,
            "edit_mode": True,
            "item": item,
            "categories": Category.objects.all().order_by("name"),
            "open_category_popup": request.GET.get("manage_category") == "1",
        },
    )

@login_required
@user_passes_test(is_superuser)
def delete_item(request, item_id):

    item = get_object_or_404(Item, id=item_id)

    if item.image and default_storage.exists(item.image.name):
        default_storage.delete(item.image.name)

    item.delete()

    messages.success(request, "Item deleted successfully.")

    return redirect("menu:menu_list")

@login_required
@user_passes_test(is_superuser)
def add_category(request):

    if request.method == "POST":

        form = CategoryForm(request.POST)

        if form.is_valid():

            category = form.save()

            return JsonResponse({

                "success": True,
                "id": category.id,
                "name": category.name

            })

        return JsonResponse({

            "success": False,
            "errors": form.errors

        })

    return JsonResponse({"success": False})


@login_required
@user_passes_test(is_superuser)
def delete_category(request):

    if request.method == "POST":

        category = get_object_or_404(
            Category,
            id=request.POST.get("category")
        )

        if category.items.exists():

            return JsonResponse({
                "success": False,
                "message": "Category contains items."
            })

        category.delete()

        return JsonResponse({
            "success": True
        })

    return JsonResponse({"success": False})

@login_required
@user_passes_test(is_superuser)
def update_category(request):

    if request.method == "POST":

        category = get_object_or_404(
            Category,
            id=request.POST.get("category")
        )

        new_name = request.POST.get("name", "").strip()

        if new_name:
            category.name = new_name

        category.show_on_home = (
            request.POST.get("show_on_home") == "true"
        )

        category.save()

        return JsonResponse({
            "success": True,
            "id": category.id,
            "name": category.name,
            "show_on_home":category.show_on_home
        })

    return JsonResponse({"success": False})


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



@login_required
def add_to_cart(request,item_id):

    item=get_object_or_404(Item,id=item_id)

    cart,created=Cart.objects.get_or_create(
        user=request.user,
        item=item,
        defaults={"quantity":1}
    )

    if not created:
        cart.quantity+=1
        cart.save()

    count=Cart.objects.filter(user=request.user).count()

    return JsonResponse({

        "success":True,
        "count":count

    })