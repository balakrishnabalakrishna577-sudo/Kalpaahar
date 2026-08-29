from django.contrib import admin
from django.utils.html import format_html
from .models import Order, PaymentRecord
from .views import _send_ebook_email, EBOOK_FILES, COMBO_FILES, BONUS_ID
import logging

logger = logging.getLogger(__name__)


def resend_ebook_action(modeladmin, request, queryset):
    """Admin action: manually re-send eBook email for selected paid orders."""
    sent = 0
    skipped = 0
    for order in queryset:
        if order.status != Order.STATUS_PAID:
            skipped += 1
            continue
        ebook_id = order.ebook_id
        if ebook_id in EBOOK_FILES and ebook_id != BONUS_ID:
            ids_to_send = [ebook_id]
        elif ebook_id in COMBO_FILES:
            ids_to_send = list(COMBO_FILES[ebook_id])
        else:
            skipped += 1
            continue
        if BONUS_ID not in ids_to_send:
            ids_to_send.append(BONUS_ID)
        try:
            _send_ebook_email(order.customer_email, order.customer_name or "Customer", ids_to_send, ebook_id)
            order.ebook_delivered = True
            order.save()
            sent += 1
        except Exception as e:
            logger.error("Manual resend failed for order %s: %s", order.razorpay_order_id, e)
            skipped += 1

    modeladmin.message_user(request, f"Sent: {sent}  |  Skipped/errors: {skipped}")


resend_ebook_action.short_description = "📧 Re-send eBook email"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "razorpay_order_id", "customer_name", "customer_email",
        "ebook_id", "amount_display", "status_badge", "ebook_delivered",
        "payment_type", "created_at",
    ]
    list_filter    = ["status", "ebook_delivered", "payment_type"]
    search_fields  = ["razorpay_order_id", "customer_email", "customer_name", "ebook_id"]
    ordering       = ["-created_at"]
    readonly_fields = [
        "razorpay_order_id", "razorpay_payment_id", "razorpay_signature",
        "created_at", "paid_at",
    ]
    actions = [resend_ebook_action]

    fieldsets = (
        ("Order",       {"fields": ("razorpay_order_id", "payment_type", "service", "ebook_id", "amount", "status", "ebook_delivered")}),
        ("Customer",    {"fields": ("customer_name", "customer_email", "customer_phone", "user")}),
        ("Razorpay",    {"fields": ("razorpay_payment_id", "razorpay_signature")}),
        ("Timestamps",  {"fields": ("created_at", "paid_at")}),
    )

    def amount_display(self, obj):
        return f"₹{obj.amount}"
    amount_display.short_description = "Amount"

    def status_badge(self, obj):
        colours = {
            "created": "#f0ad4e",
            "paid":    "#5cb85c",
            "failed":  "#d9534f",
        }
        colour = colours.get(obj.status, "#aaa")
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 10px;border-radius:999px;font-size:.8rem;font-weight:600">{}</span>',
            colour, obj.status.upper()
        )
    status_badge.short_description = "Status"


@admin.register(PaymentRecord)
class PaymentRecordAdmin(admin.ModelAdmin):
    list_display   = ["payment_id", "order", "verified_at"]
    search_fields  = ["payment_id"]
    readonly_fields = ["verified_at"]
    ordering       = ["-verified_at"]
