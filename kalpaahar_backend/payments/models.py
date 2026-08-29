from django.db import models
from django.conf import settings


class Order(models.Model):
    STATUS_CREATED = "created"
    STATUS_PAID    = "paid"
    STATUS_FAILED  = "failed"
    STATUS_CHOICES = [
        (STATUS_CREATED, "Created"),
        (STATUS_PAID,    "Paid"),
        (STATUS_FAILED,  "Failed"),
    ]

    # Razorpay identifiers
    razorpay_order_id   = models.CharField(max_length=100, unique=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True)
    razorpay_signature  = models.CharField(max_length=300, blank=True)

    # Product info
    ebook_id     = models.CharField(max_length=100, blank=True)
    payment_type = models.CharField(max_length=50, default="ebook")   # "ebook" | "consultation"
    service      = models.CharField(max_length=200, blank=True)

    # Customer info (captured at checkout even for anonymous users)
    customer_name  = models.CharField(max_length=200, blank=True)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20, blank=True)

    # Amount in rupees (not paise)
    amount = models.IntegerField()

    # State
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_CREATED)
    ebook_delivered = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at    = models.DateTimeField(null=True, blank=True)

    # Optional link to registered user
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="orders",
    )

    class Meta:
        ordering       = ["-created_at"]
        verbose_name   = "Order"
        verbose_name_plural = "Orders"

    def __str__(self):
        return f"{self.razorpay_order_id} — {self.customer_email} — ₹{self.amount} [{self.status}]"


class PaymentRecord(models.Model):
    """Created once a payment is successfully verified client-side."""

    order        = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment_record")
    payment_id   = models.CharField(max_length=100)
    signature    = models.CharField(max_length=300)
    verified_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Payment Record"
        verbose_name_plural = "Payment Records"

    def __str__(self):
        return f"{self.payment_id} (Order: {self.order.razorpay_order_id})"
