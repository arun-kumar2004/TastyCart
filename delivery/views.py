from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse, HttpResponseForbidden
from django.conf import settings
from django.core.mail import send_mail
from django.contrib import messages
from datetime import timedelta
import random, string
import pytz

from orders.models import Order

OTP_LENGTH = 6
OTP_EXPIRE_MINUTES = 10


def _is_service_user(user):
    return user.is_superuser or user.groups.filter(name="service_provider").exists()


@login_required
def delivery_view(request):
    ist = pytz.timezone("Asia/Kolkata")
    now = timezone.localtime(timezone.now(), ist)

    if _is_service_user(request.user):
        orders = Order.objects.order_by("confirmed_at")
    else:
        orders = Order.objects.filter(user=request.user).order_by("confirmed_at")

    if not orders.exists() and not _is_service_user(request.user):
        messages.info(request, "You have no order yet.")
        return redirect("home")

    return render(request, "delivery/delivery.html", {
        "orders": orders,
        "is_service_user": _is_service_user(request.user),
        "now_ts": int(now.timestamp()),
        "is_admin": request.user.is_superuser
    })


# ----------------- OTP HANDLING -----------------
@login_required
def send_delivery_otp(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # Restriction: if user is cancelling, check left_time
    if request.user == order.user and order.left_time is not None:
        if order.left_time < 1800:  # less than 30 mins
            return JsonResponse({"success": False, "error": "Now you can't cancel your order"})
        else:
            # confirmation handled on frontend (popup)
            pass

    if not (_is_service_user(request.user) or request.user == order.user):
        return HttpResponseForbidden("Not allowed")

    otp = "".join(random.choices(string.digits, k=OTP_LENGTH))
    expiry = timezone.now() + timedelta(minutes=OTP_EXPIRE_MINUTES)
    order.delivery_otp = otp
    order.delivery_otp_expiry = expiry
    order.save()

    ist = pytz.timezone("Asia/Kolkata")
    expiry_ist = expiry.astimezone(ist)

    subject = f"TastyCart: OTP for Order #{order.id}"
    html = f"""
    <div style="font-family: Arial, sans-serif; color:#333;">
      <p><strong style="color:#2563eb;">Hello {order.user.get_full_name() or order.user.username},</strong></p>
      <p>Your delivery OTP is:</p>
      <p style="font-size:20px; font-weight:bold; color:#0b61ff;">{otp}</p>
      <p style="color:#6b7280;">This code will expire at {expiry_ist.strftime('%I:%M %p')} IST.</p>
      <p style="margin-top:12px; color:#333;">
        If this is not you, you can ignore this email.
        For issues contact admin: <a href="mailto:{settings.CONTACT_US_EMAIL}">{settings.CONTACT_US_EMAIL}</a>
      </p>
      <hr>
      <p style="text-align:right; color:#2563eb; font-weight:bold;">Thank you ❤️ TastyCart ❤️❤️</p>
    </div>
    """

    try:
        send_mail(subject, "", settings.CONTACT_US_EMAIL, [order.user.email], html_message=html)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": True, "message": "OTP sent successfully"})


@login_required
def verify_delivery_otp(request, order_id):
    if request.method !="POST":
        return JsonResponse({"success": False, "error": "POST required"}, status=400)

    order = get_object_or_404(Order, id=order_id)
    otp = (request.POST.get("otp") or "").strip()

    if not order.delivery_otp or not order.delivery_otp_expiry:
        return JsonResponse({"success": False, "error": "No OTP generated"}, status=400)

    if timezone.now() > order.delivery_otp_expiry:
        return JsonResponse({"success": False, "error": "OTP expired"}, status=400)

    if otp != order.delivery_otp:
        return JsonResponse({"success": False, "error": "Invalid OTP"}, status=400)

    ist = pytz.timezone("Asia/Kolkata")

    # Case 1: Admin verifies (Order Completed)
    if _is_service_user(request.user):
        order.status = "completed"
        order.delivered = True
        order.delivered_at = timezone.now()
        order.left_time = 0
        order.delivery_otp = None
        order.delivery_otp_expiry = None
        order.save()
        return JsonResponse({"success": True, "status": "completed", "delivered_at": order.delivered_at.astimezone(ist).strftime("%I:%M %p")})

    # Case 2: User verifies (Cancel Order)
    elif request.user == order.user:
        order.status = "cancelled"
        order.cancelled_by = f"user ({request.user.username})"
        order.cancelled_at = timezone.now()
        order.left_time = 0
        order.delivery_otp = None
        order.delivery_otp_expiry = None
        order.save()
        return JsonResponse({"success": True, "status": "cancelled", "cancelled_by": order.cancelled_by})

    return HttpResponseForbidden("Not allowed")


# ----------------- ADMIN CONTROLS -----------------
@login_required
def delete_order(request, order_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Only admin can delete orders")
    order = get_object_or_404(Order, id=order_id)
    order.delete()
    return JsonResponse({"success": True, "message": f"Order #{order_id} deleted permanently"})

# delivery/views.py
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.utils import timezone

import pytz

def update_order_status(request, order_id):
    if request.method == "POST":
        order = get_object_or_404(Order, pk=order_id)
        status = request.POST.get("status")

        ist = pytz.timezone("Asia/Kolkata")
        now_ist = timezone.localtime(timezone.now(), ist)

        if status not in dict(Order.STATUS_CHOICES):
            return JsonResponse({"success": False, "error": "Invalid status"})

        order.status = status

        if status == "on_the_way":
            order.actual_delivery_time = now_ist + timedelta(minutes=30)
            order.left_time = 30 * 60  # store remaining time in seconds
        elif status == "completed":
            order.delivered = True
            order.delivered_at = now_ist
        elif status == "cancelled":
            cancelled_by = "user" if request.user == order.user else "admin"
            order.cancelled_by = f"{cancelled_by} ({request.user.username})"

        order.save()
        return JsonResponse({"success": True, "status": order.status})
    return JsonResponse({"success": False, "error": "Invalid request method"})
    
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import random


# ----------------- CANCEL OTP -----------------
cancel_otps = {}  # temporary storage for OTPs

def send_cancel_otp(request, order_id):
    if request.method == "GET":
        otp = str(random.randint(1000, 9999))
        cancel_otps[order_id] = otp
        order = Order.objects.get(id=order_id)

        subject = f"TastyCart: OTP to Cancel Your Order #{order.id}"
        html_message = f"""
        <div style="font-family: Arial, sans-serif; color:#333;">
          <p><strong style="color:#2563eb;">Hello {order.user.get_full_name() or order.user.username},</strong></p>
          <p>We received a request to cancel your order <strong>#{order.id}</strong>.</p>
          <p>Your OTP to confirm the cancellation is:</p>
          <p style="font-size:20px; font-weight:bold; color:#0b61ff;">{otp}</p>
          <p style="color:#6b7280;">⚠️ This OTP is valid for 10 minutes only.</p>
          <p style="margin-top:12px; color:#333;">
            If you did NOT request this cancellation, please ignore this email. Your order will remain active.
          </p>
          <hr>
          <p style="text-align:right; color:#2563eb; font-weight:bold;">Thank you<br>TastyCart Team ❤️❤️</p>
        </div>
        """

        try:
            send_mail(subject, "", settings.CONTACT_US_EMAIL, [order.user.email], html_message=html_message)
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

        return JsonResponse({"success": True, "message": "Cancel OTP sent to your email", "email": order.user.email})
    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)


@csrf_exempt
def verify_cancel_otp(request, order_id):
    if request.method == "POST":
        import json
        data = json.loads(request.body)
        otp = data.get("otp")
        order = Order.objects.get(id=order_id)

        # Check OTP
        if cancel_otps.get(order_id) == otp:
            # User cancelled via OTP
            order.status = "cancelled"
            order.cancelled_by = f"user ({order.user.username})"  # store who cancelled
            order.save()
            cancel_otps.pop(order_id, None)
            return JsonResponse({
                "success": True,
                "message": f"Order cancelled successfully by {order.cancelled_by}"
            })
        
        return JsonResponse({"success": False, "error": "Invalid OTP"})
    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)


