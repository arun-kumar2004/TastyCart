from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import pytz

class Order(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_ON_THE_WAY = 'on_the_way'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_ON_THE_WAY, 'On the way'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        help_text="Order status: pending / on_the_way / completed / cancelled"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders"
    )
    confirmed_at = models.DateTimeField(default=timezone.now)

    eta_minutes = models.PositiveIntegerField(default=30)
    estimate_delivery_time = models.DateTimeField(blank=True, null=True)
    actual_delivery_time = models.DateTimeField(blank=True, null=True)

    delivery_otp = models.CharField(max_length=16, blank=True, null=True)
    delivery_otp_expiry = models.DateTimeField(blank=True, null=True)

    delivered = models.BooleanField(default=False)
    delivered_at = models.DateTimeField(blank=True, null=True)

    grand_total = models.DecimalField(max_digits=12, decimal_places=2)

    cancelled_by = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Stores 'user (username)' or 'admin' if cancelled"
    )

    def save(self, *args, **kwargs):
        ist = pytz.timezone("Asia/Kolkata")

        # Ensure confirmed_at is timezone aware
        if self.confirmed_at and timezone.is_naive(self.confirmed_at):
            self.confirmed_at = timezone.make_aware(self.confirmed_at, ist)

        # Set estimate_delivery_time if not already set
        if not self.estimate_delivery_time:
            self.estimate_delivery_time = self.confirmed_at + timedelta(minutes=self.eta_minutes)

        # Set actual_delivery_time only if new object
        if not self.id and not self.actual_delivery_time:
            self.actual_delivery_time = self.estimate_delivery_time

        # Localize datetime fields to IST
        if self.estimate_delivery_time:
            self.estimate_delivery_time = timezone.localtime(self.estimate_delivery_time, ist)
        if self.actual_delivery_time:
            self.actual_delivery_time = timezone.localtime(self.actual_delivery_time, ist)

        super().save(*args, **kwargs)

    def is_otp_valid(self, otp):
        """Check if given OTP is valid and not expired."""
        return self.delivery_otp == otp and self.delivery_otp_expiry and self.delivery_otp_expiry > timezone.now()

    def __str__(self):
        return f"Order #{self.id} ({self.status}) by {getattr(self.user, 'username', str(self.user))}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    image = models.URLField(blank=True, null=True)

    @property
    def total(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.name}"

# from django.db import models
# from django.conf import settings
# from django.utils import timezone
# from datetime import timedelta
# import pytz


# class Order(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
#     confirmed_at = models.DateTimeField(default=timezone.now)

#     # estimated minutes from confirmation (e.g. 90)
#     eta_minutes = models.PositiveIntegerField(default=30)

#     # stored datetimes
#     estimate_delivery_time = models.DateTimeField(blank=True, null=True)  # confirmed_at + eta_minutes
#     actual_delivery_time = models.DateTimeField(blank=True, null=True)    # if you have extra buffer/time

#     # OTP & delivery state (admin/service-provider will use delivery_otp)
#     delivery_otp = models.CharField(max_length=16, blank=True, null=True)
#     delivery_otp_expiry = models.DateTimeField(blank=True, null=True)

#     delivered = models.BooleanField(default=False)
#     delivered_at = models.DateTimeField(blank=True, null=True)  # when order will be removed (set after OTP)

#     grand_total = models.DecimalField(max_digits=12, decimal_places=2)

#     def save(self, *args, **kwargs):
#         ist = pytz.timezone("Asia/Kolkata")

#         # ensure confirmed_at is IST
#         if self.confirmed_at and timezone.is_naive(self.confirmed_at):
#             self.confirmed_at = timezone.make_aware(self.confirmed_at, ist).astimezone(ist)

#         # auto-set estimate & actual datetimes if not provided
#         if not self.estimate_delivery_time:
#             self.estimate_delivery_time = self.confirmed_at + timedelta(minutes=self.eta_minutes)
#         if not self.actual_delivery_time:
#             self.actual_delivery_time = self.estimate_delivery_time

#         # convert estimate & actual to IST
#         if self.estimate_delivery_time:
#             self.estimate_delivery_time = timezone.localtime(self.estimate_delivery_time, ist)
#         if self.actual_delivery_time:
#             self.actual_delivery_time = timezone.localtime(self.actual_delivery_time, ist)

#         super().save(*args, **kwargs)

#     def eta_datetime(self):
#         return self.estimate_delivery_time

#     def seconds_until_delivery(self):
#         """
#         Signed seconds left:
#           positive -> seconds until delivery
#           negative -> seconds since scheduled delivery (late)
#         """
#         delta = (self.actual_delivery_time - timezone.localtime(timezone.now(), pytz.timezone("Asia/Kolkata"))).total_seconds()
#         return int(delta)

#     def remaining_seconds(self):
#         # non-negative remaining seconds for UI that should not show negatives
#         return int(max(0, self.seconds_until_delivery()))

#     def is_expired(self):
#         # treat as expired when actual time passed and not delivered (this doesn't auto-delete)
#         return self.seconds_until_delivery() <= 0 and not self.delivered

#     def __str__(self):
#         return f"Order #{self.id} by {getattr(self.user, 'username', str(self.user))}"


# class OrderItem(models.Model):
#     order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
#     name = models.CharField(max_length=255)
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     quantity = models.PositiveIntegerField(default=1)
#     image = models.URLField(blank=True, null=True)

#     @property
#     def total(self):
#         return self.price * self.quantity

#     def __str__(self):
#         return f"{self.quantity} x {self.name}"
    
    
# # orders/models.py
# from django.db import models
# from django.conf import settings
# from django.utils import timezone
# from datetime import timedelta


# class Order(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
#     confirmed_at = models.DateTimeField(default=timezone.now)

#     # minutes estimated from confirmation
#     eta_minutes = models.PositiveIntegerField(default=30)

#     # stored datetimes
#     estimate_delivery_time = models.DateTimeField(blank=True, null=True)
#     actual_delivery_time = models.DateTimeField(blank=True, null=True)

#     # OTP & delivery state (for admin/service-provider flow)
#     delivery_otp = models.CharField(max_length=16, blank=True, null=True)
#     delivery_otp_expiry = models.DateTimeField(blank=True, null=True)

#     delivered = models.BooleanField(default=False)
#     delivered_at = models.DateTimeField(blank=True, null=True)  # when order will be deleted (now + 10s) after OTP verify

#     grand_total = models.DecimalField(max_digits=12, decimal_places=2)

#     def save(self, *args, **kwargs):
#         # ensure estimate & actual times are set
#         if not self.estimate_delivery_time:
#             self.estimate_delivery_time = self.confirmed_at + timedelta(minutes=self.eta_minutes)
#         if not self.actual_delivery_time:
#             # by default set actual same as estimate (you can change if you want different logic)
#             self.actual_delivery_time = self.estimate_delivery_time
#         super().save(*args, **kwargs)

#     def eta_datetime(self):
#         return self.estimate_delivery_time

#     def seconds_until_delivery(self):
#         """
#         Signed seconds left: positive -> seconds until delivery
#         negative -> seconds since it should have arrived (late)
#         """
#         delta = (self.actual_delivery_time - timezone.now()).total_seconds()
#         return int(delta)

#     def remaining_seconds(self):
#         "Non-negative remaining seconds (used where you want no negative values)."
#         return int(max(0, self.seconds_until_delivery()))

#     def is_expired(self):
#         # we don't auto-delete immediately; this returns True when actual_delivery_time < now
#         return self.seconds_until_delivery() <= 0 and not self.delivered

#     def __str__(self):
#         return f"Order #{self.id} by {self.user.username}"


# class OrderItem(models.Model):
#     order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
#     name = models.CharField(max_length=255)
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     quantity = models.PositiveIntegerField(default=1)
#     image = models.URLField(blank=True, null=True)

#     @property
#     def total(self):
#         return self.price * self.quantity

#     def __str__(self):
#         return f"{self.quantity} x {self.name}"