
# orders/views.py

from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.utils import timezone
from cart.models import Cart  # best-effort cleanup of cart items (may be absent/different on some projects)
import random, string, datetime, pytz
from decimal import Decimal
from .models import Order, OrderItem
from django.contrib.auth import get_user_model
from django.urls import reverse


User = get_user_model()


CODE_LENGTH = 6
CODE_EXPIRY_MINUTES = 10
IST = pytz.timezone("Asia/Kolkata")


def _generate_code(n=CODE_LENGTH):
    """Return numeric code of length n."""
    return "".join(random.choices(string.digits, k=n))




@login_required
def order_view(request):
    """
    Build pending order from session, validate quantities and user profile,
    generate a verification code and send it to user's email.
    """
    pending = request.session.get("pending_order")
    if not pending:
        messages.error(request, "No items selected. Please add items from cart.")
        return redirect("cart:cart")

    back_url = request.META.get("HTTP_REFERER", None)
    if not back_url or "order" in back_url:
        back_url = "/cart/"

    if request.method == "POST":
        # Validate user profile fields (phone_no and address used elsewhere in templates)
        # If missing, ask user to update them first.
        if not getattr(request.user, "phone", None) or not getattr(request.user, "address", None):
            messages.error(request, "Please update your phone number and address before confirming your order.")
            # use direct path to avoid reversing issues (projects often use /users/signup/ or similar)
            return redirect(reverse("update_profile"))

        selected_ids = request.POST.getlist("selected_items")
        updated_items, grand_total = [], Decimal("0.00")

        for item in pending.get("items", []):
            if str(item.get("id", "")) in selected_ids:
                raw_qty = request.POST.get(f"qty_{item['id']}", "").strip()
                try:
                    qty = int(raw_qty) if raw_qty != "" else 0
                except ValueError:
                    qty = 0
                if qty < 1:
                    messages.error(request, f"Please select a valid quantity for {item['name']}.")
                    return redirect("orders:order")

                item["quantity"] = qty
                # item['price'] might be Decimal/string/float; ensure proper arithmetic
                item_price = Decimal(str(item.get("price", "0")))
                item_total = (item_price * qty).quantize(Decimal("0.01"))
                item["total"] = float(item_total)  # keep session-friendly simple type
                updated_items.append(item)
                grand_total += item_total

        if not updated_items:
            messages.error(request, "Please select at least one item.")
            return redirect("orders:order")

        pending["items"] = updated_items
        pending["grand_total"] = float(grand_total.quantize(Decimal("0.01")))

        # generate verification code and expiry (in IST)
        code = _generate_code()
        expiry_dt = timezone.localtime(timezone.now(), IST) + datetime.timedelta(minutes=CODE_EXPIRY_MINUTES)
        expiry_ts = expiry_dt.timestamp()
        pending["code"] = code
        pending["expiry_ts"] = expiry_ts
        request.session["pending_order"] = pending
        request.session.modified = True

        # send verification code email (simple, professional HTML)
        user_email = request.user.email or ""
        if user_email:
            html_message = f"""
                <div style="font-family: Arial, sans-serif; color:#333; line-height:1.6;">
                    <p><strong style="color:#2563eb;">Hello {request.user.get_full_name() or request.user.username},</strong></p>
                    <p>Your verification code to confirm your order is:</p>
                    <p style="font-size:20px; font-weight:bold; color:#dc2626;">{code}</p>
                    <p style="color:#6b7280;">(This code will expire in {CODE_EXPIRY_MINUTES} minutes)</p>
                    <hr style="margin:20px 0; border:none; border-top:1px solid #ccc;">
                    <p style="margin-top:20px; color:#555;">
                        👉 If this is not you, ignore this email.<br>
                        For issues contact admin at <span style="color:#2563eb;">{settings.CONTACT_US_EMAIL}</span>
                    </p>

                    <hr style="margin:20px 0; border:none; border-top:1px solid #ccc;">
                    <p style="text-align:right; color:#2563eb; font-weight:bold;">Thank you ❤️ TastyCart ❤️❤️</p>
                </div>
            """
            try:
                send_mail(
                    subject="Your TastyCart verification code",
                    message="",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user_email],
                    fail_silently=False,
                    html_message=html_message,
                )
            except Exception as e:
                messages.error(request, f"Failed to send verification email: {e}")
                return redirect("orders:order")

        messages.success(request, f"A verification code was sent to {user_email or 'your email'}.")
        return redirect("orders:verify")

    return render(request, "orders/order_form.html", {
        "items": pending.get("items", []),
        "grand_total": pending.get("grand_total", 0),
        "back_url": back_url,
    })


@login_required
def verify_code(request):
    """
    User posts the verification code emailed to them.
    On success:
      - create an Order and OrderItems in DB,
      - calculate & store estimate_delivery_time and actual_delivery_time,
      - clear pending session and cart items,
      - send a confirmation email with a table that includes header (Sr No, Item Name, Quantity, Price, Total),
      - redirect to order success page (order id passed).
    """
    pending = request.session.get("pending_order")
    if not pending:
        messages.error(request, "No pending order found. Please create an order first.")
        return redirect("orders:order")

    if request.method == "POST":
        submitted = (request.POST.get("code") or "").strip()
        if not submitted:
            messages.error(request, "Enter the verification code sent to your email.")
            return redirect("orders:verify")

        # compare expiry using IST-based now
        now_ts = timezone.localtime(timezone.now(), IST).timestamp()
        if now_ts > float(pending.get("expiry_ts", 0)):
            messages.error(request, "Code expired. Please resend the code.")
            return redirect("orders:verify")

        if submitted != str(pending.get("code")):
            messages.error(request, "Invalid verification code. Try again or resend.")
            return redirect("orders:verify")

        # code valid -> create DB Order and OrderItems
        # ETA generated between 30 and 90 minutes (per your last instruction)
        eta_minutes = random.randint(30, 90)
        confirmed_at = timezone.localtime(timezone.now(), IST)
        arrival_time = confirmed_at + datetime.timedelta(minutes=eta_minutes)

        # create order and store both estimate_delivery_time and actual_delivery_time
        order = Order.objects.create(
            user=request.user,
            confirmed_at=confirmed_at,
            eta_minutes=eta_minutes,
            estimate_delivery_time=arrival_time,
            actual_delivery_time=arrival_time,
            grand_total=Decimal(str(pending.get("grand_total", "0.00"))),
        )

        # create OrderItem rows
        for it in pending.get("items", []):
            OrderItem.objects.create(
                order=order,
                name=it.get("name", ""),
                price=Decimal(str(it.get("price", "0"))),
                quantity=int(it.get("quantity", 1)),
                image=it.get("image", "") or None
            )

        # persist / ensure datetimes exist (Order.save logic in model may set defaults)
        order.save()

        # remove pending order from session
        request.session.pop("pending_order", None)
        request.session.modified = True

        # remove related cart items in DB if id list present
        item_ids = [it.get("id") for it in pending.get("items", []) if it.get("id")]
        if item_ids:
            try:
                Cart.objects.filter(user=request.user, item_id__in=item_ids).delete()
            except Exception:
                # best-effort cleanup: do not fail the order flow if cart model is different
                pass

        # build email with header + rows (guaranteed from DB items)
        eta_dt = order.estimate_delivery_time
        arrival_str = timezone.localtime(eta_dt, IST).strftime("%I:%M %p") if eta_dt else "-"

        table_header = """
            <thead>
                <tr style="background:#f3f4f6; text-align:center; font-weight:bold;">
                    <th style="padding:8px; border-bottom:2px solid #ddd;">Sr No</th>
                    <th style="padding:8px; border-bottom:2px solid #ddd;">Item Name</th>
                    <th style="padding:8px; border-bottom:2px solid #ddd;">Quantity</th>
                    <th style="padding:8px; border-bottom:2px solid #ddd;">Price</th>
                    <th style="padding:8px; border-bottom:2px solid #ddd;">Total</th>
                </tr>
            </thead>
        """

        table_rows = ""
        for i, db_it in enumerate(order.items.all()):
            # db_it.total uses model property (Decimal * int) - show with 2 decimals
            price_str = f"{db_it.price:.2f}"
            total_str = f"{(db_it.price * db_it.quantity):.2f}"
            table_rows += f"""
                <tr style='border-bottom:1px solid #ddd;'>
                    <td style='padding:8px; text-align:center;'>{i+1}</td>
                    <td style='padding:8px; color:#2563eb; font-weight:bold;'>{db_it.name}</td>
                    <td style='padding:8px; text-align:center;'>{db_it.quantity}</td>
                    <td style='padding:8px; text-align:center;'>₹{price_str}</td>
                    <td style='padding:8px; text-align:center; color:#16a34a;'>₹{total_str}</td>
                </tr>
            """

        html_message = f"""
            <div style="font-family: Arial, sans-serif; color:#333; line-height:1.6;">
                <p><strong style="color:#2563eb;">Hello {request.user.get_full_name() or request.user.username},</strong></p>
                <p>Your order <strong>#{order.id}</strong> is confirmed.</p>
                <p><strong>Arrival time:</strong> {arrival_str} (in {eta_minutes} minutes)</p>

                <h3 style="margin-top:20px; color:#111;">Order Summary:</h3>
                <table style="width:100%; border-collapse:collapse; margin-top:10px; font-size:14px;">
                    {table_header}
                    <tbody>
                        {table_rows}
                        <tr>
                            <td colspan="4" style="padding:8px; text-align:right; font-weight:bold; color:#9333ea;">Grand Total</td>
                            <td style="padding:8px; text-align:center; font-weight:bold; color:#9333ea;">₹{order.grand_total:.2f}</td>
                        </tr>
                    </tbody>
                </table>

                <p style="margin-top:20px; color:#555;">
                    👉 If this is not you, ignore this email.<br>
                    For issues contact admin at <span style="color:#2563eb;">{settings.CONTACT_US_EMAIL}</span>
                </p>

                <hr style="margin:20px 0; border:none; border-top:1px solid #ccc;">
                <p style="text-align:right; color:#2563eb; font-weight:bold;">Thank you ❤️ TastyCart ❤️❤️</p>
            </div>
        """

        # send confirmation email (best-effort)
        if request.user.email:
            try:
                send_mail(
                    subject=f"TastyCart: Order #{order.id} confirmed",
                    message="",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[request.user.email],
                    fail_silently=True,
                    html_message=html_message
                )
            except Exception:
                # do not break flow on email problems
                pass

        messages.success(request, "Order confirmed. Check the email for details.")
        # redirect to order success passing the DB order id — order_success view will load DB record
        return redirect("orders:success", order_id=order.id)

    # GET -> render verification page
    return render(request, "orders/verify_code.html", {"pending": pending})


@login_required
def resend_code(request):
    """
    Regenerate the verification code and send to user's email.
    This only applies to session-based pending orders (before DB order creation).
    """
    pending = request.session.get("pending_order")
    if not pending:
        messages.error(request, "No pending order to resend the code for.")
        return redirect("orders:order")

    code = _generate_code()
    pending["code"] = code
    expiry_dt = timezone.localtime(timezone.now(), IST) + datetime.timedelta(minutes=CODE_EXPIRY_MINUTES)
    pending["expiry_ts"] = expiry_dt.timestamp()
    request.session["pending_order"] = pending
    request.session.modified = True

    user_email = request.user.email
    subject = "Your TastyCart verification code (resend)"
    body = f"Your new verification code is: {code}\nIt will expire in {CODE_EXPIRY_MINUTES} minutes.\n\n👉 If this is not you, ignore this email.\nFor issues contact admin at {settings.CONTACT_US_EMAIL}\n\nThank you ❤️ TastyCart ❤️❤️"
    try:
        if user_email:
            send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [user_email], fail_silently=False)
        messages.success(request, "A new verification code was sent to your email.")
    except Exception as e:
        messages.error(request, f"Failed to send email: {e}")

    return redirect("orders:verify")


@login_required
def order_success(request, order_id):
    """
    Load the order from DB and render success page.
    We explicitly pass `actual_ts` (unix seconds) so templates/JS will always show arrival time
    derived from DB (consistent across pages).
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # ensure the saved datetimes are present (Order.save may set defaults)
    if not order.estimate_delivery_time or not order.actual_delivery_time:
        order.save()

    actual_ts = None
    if order.actual_delivery_time:
        # convert to unix seconds for JS consumption (IST)
        actual_ts = int(order.actual_delivery_time.astimezone(IST).timestamp())

    return render(request, "orders/order_success.html", {
        "order": order,
        "actual_ts": actual_ts
    })
    

