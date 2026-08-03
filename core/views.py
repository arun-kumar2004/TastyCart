from django.shortcuts import render
from menu.models import Item
from cart.models import Cart

from django.shortcuts import render
from django.db.models import Prefetch

from menu.models import Category, Item
from cart.models import Cart


def home(request):

    # Categories selected for Home
    home_categories = (
        Category.objects.filter(show_on_home=True)
        .prefetch_related(
            Prefetch(
                "items",
                queryset=Item.objects.filter(
                    popular=True
                )
                .exclude(name__isnull=True)
                .exclude(name__exact="")
                .order_by("-updated_at"),
            )
        )
        .order_by("name")
    )

    # Cart items
    if request.user.is_authenticated:
        cart_ids = list(
            Cart.objects.filter(user=request.user)
            .values_list("item_id", flat=True)
        )
    else:
        cart_ids = []

    context = {
        "home_categories": home_categories,
        "cart_ids": cart_ids,
    }

    return render(request, "home.html", context)

