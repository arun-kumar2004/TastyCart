from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count, Sum
from django.db.models.functions import Coalesce

from menu.models import Item, Category
from core.models import CustomUser
from cart.models import Cart
from orders.models import Order
from decimal import Decimal

from django.db.models import Sum, DecimalField, Value
from django.db.models.functions import Coalesce

# ==========================================================
# Super Admin Check
# ==========================================================

def is_superuser(user):
    return user.is_authenticated and user.is_superuser


# ==========================================================
# Dashboard
# ==========================================================

@user_passes_test(is_superuser)
def dashboard(request):

    # ------------------------------------------------------
    # Products
    # ------------------------------------------------------

    products = (
        Item.objects
        .select_related("category")
        .order_by("-created_at")
    )

    recent_products = (
        Item.objects
        .select_related("category")
        .order_by("-created_at")[:10]
    )

    featured_products = (
        Item.objects
        .filter(popular=True)
        .select_related("category")
    )

    # ------------------------------------------------------
    # Categories
    # ------------------------------------------------------

    categories = (
        Category.objects
        .annotate(
            product_count=Count("items")
        )
        .order_by("name")
    )

    # ------------------------------------------------------
    # Users
    # ------------------------------------------------------

    customers = (
        CustomUser.objects
        .filter(is_superuser=False)
        .order_by("-date_joined")
    )

    admins = (
        CustomUser.objects
        .filter(is_superuser=True)
        .order_by("first_name")
    )

    # ------------------------------------------------------
    # Orders
    # ------------------------------------------------------

    orders = (
        Order.objects
        .order_by("-id")
    )

    # ------------------------------------------------------
    # Cart
    # ------------------------------------------------------

    carts = (
        Cart.objects
        .select_related(
            "user",
            "item"
        )
    )

    # ------------------------------------------------------
    # Statistics
    # ------------------------------------------------------

    total_products = products.count()

    total_categories = categories.count()

    total_customers = customers.count()

    total_admins = admins.count()

    total_orders = orders.count()

    total_featured_products = featured_products.count()

    total_cart_items = carts.count()

    total_product_price = (
    Item.objects.aggregate(
        total=Coalesce(
            Sum("price"),
            Value(
                Decimal("0.00"),
                output_field=DecimalField(
                    max_digits=10,
                    decimal_places=2
                )
            )
        )
    )["total"]
)

    # ------------------------------------------------------
    # Category Statistics
    # ------------------------------------------------------

    category_chart_labels = []

    category_chart_values = []

    for category in categories:

        category_chart_labels.append(
            category.name
        )

        category_chart_values.append(
            category.product_count
        )

    # ------------------------------------------------------
    # Featured Category Count
    # ------------------------------------------------------

    featured_category_count = 0

    for category in categories:

        home_items = (
            Item.objects.filter(
                category=category,
                popular=True
            ).count()
        )

        category.home_products = home_items

        if home_items > 0:
            featured_category_count += 1

    # ------------------------------------------------------
    # Context
    # ------------------------------------------------------

    context = {

        # Logged In Admin
        "admin": request.user,

        # Products
        "products": products,
        "recent_products": recent_products,
        "featured_products": featured_products,

        # Categories
        "categories": categories,

        # Users
        "customers": customers,
        "admins": admins,

        # Orders
        "orders": orders,

        # Cart
        "carts": carts,

        # Dashboard Cards
        "total_products": total_products,
        "total_categories": total_categories,
        "total_customers": total_customers,
        "total_admins": total_admins,
        "total_orders": total_orders,
        "total_featured_products": total_featured_products,
        "total_cart_items": total_cart_items,
        "total_product_price": total_product_price,
        "featured_category_count": featured_category_count,

        # Charts
        "category_chart_labels": category_chart_labels,
        "category_chart_values": category_chart_values,

    }

    return render(
        request,
        "adminpanel/dashboard.html",
        context
    )