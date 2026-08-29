import hashlib
import hmac
import json
import logging
import os
from datetime import datetime, timezone

import razorpay
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import Order, PaymentRecord

logger = logging.getLogger(__name__)

# ─── Price catalog (server-side; never trust the client amount) ───────────────
EBOOK_PRICES = {
    "high-protein-breakfast":          299,
    "picky-eaters":                    299,
    "snack-smart":                     299,
    "gut-reset":                       299,
    "power-lunch":                     299,
    "ancient-grain-modern-plate":      299,
    # collections
    "complete-kalpaahar-collection":   1299,
    "protein-&-energy-collection":     699,
    "happy-family-nutrition-collection": 699,
    "gut-&-grain-wellness-collection": 749,
}

CONSULTATION_PRICES = {
    "Quick Consultation":                    800,
    "Condition-Specific Nutrition Plan":    2500,
}

# ─── eBook → PDF filename map ─────────────────────────────────────────────────
EBOOK_FILES = {
    "high-protein-breakfast":          "High-Protein-Breakfast.pdf",
    "picky-eaters":                    "Picky-Eaters.pdf",
    "snack-smart":                     "Snack-Smart.pdf",
    "gut-reset":                       "Gut-Health-Reset.pdf",
    "power-lunch":                     "Power-Lunch.pdf",
    "ancient-grain-modern-plate":      "Ancient Grain, Modern Plate.pdf",
    "move-well-home-workout-guide":    "Move-Well-Home-Workout-Guide.pdf",
}

COMBO_FILES = {
    "complete-kalpaahar-collection": [
        "high-protein-breakfast", "gut-reset", "power-lunch",
        "snack-smart", "ancient-grain-modern-plate", "picky-eaters",
    ],
    "protein-&-energy-collection": [
        "high-protein-breakfast", "power-lunch", "snack-smart",
    ],
    "happy-family-nutrition-collection": [
        "picky-eaters", "high-protein-breakfast", "snack-smart",
    ],
    "gut-&-grain-wellness-collection": [
        "gut-reset", "ancient-grain-modern-plate", "high-protein-breakfast",
    ],
}

BONUS_ID = "move-well-home-workout-guide"


def _razorpay_client():
    return razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/orders  — Create a Razorpay order
# ─────────────────────────────────────────────────────────────────────────────
@csrf_exempt
@require_POST
def create_order(request):
    try:
        body = json.loads(request.body)
    except (ValueError, KeyError):
        return JsonResponse({"success": False, "error": "Invalid JSON body"}, status=400)

    amount       = body.get("amount")
    ebook_id     = str(body.get("ebookId", "")).strip()
    payment_type = str(body.get("paymentType", "ebook")).strip()
    service      = str(body.get("service", "")).strip()
    customer     = body.get("customer", {})

    # ── Validate amount ──────────────────────────────────────────────────────
    try:
        amount = int(amount)
    except (TypeError, ValueError):
        return JsonResponse({"success": False, "error": "Invalid amount"}, status=400)

    # ── Determine expected price ─────────────────────────────────────────────
    if payment_type == "consultation":
        if not service:
            return JsonResponse({"success": False, "error": "Service name is required for consultation"}, status=400)
        expected = CONSULTATION_PRICES.get(service)
    else:
        expected = EBOOK_PRICES.get(ebook_id)

    if expected is None:
        return JsonResponse({"success": False, "error": "Invalid product or service"}, status=400)

    if amount != expected:
        return JsonResponse(
            {"success": False, "error": "Amount mismatch",
             "expected": expected, "received": amount},
            status=400,
        )

    # ── Validate customer email for ebooks ───────────────────────────────────
    if payment_type != "consultation" and not customer.get("email"):
        return JsonResponse({"success": False, "error": "Customer email is required"}, status=400)

    # ── Create Razorpay order ────────────────────────────────────────────────
    try:
        client = _razorpay_client()
        rz_order = client.order.create({
            "amount":   expected * 100,   # paise
            "currency": "INR",
            "receipt":  f"{'consultation' if payment_type == 'consultation' else 'ebook'}_{int(datetime.now(timezone.utc).timestamp())}",
            "notes": {
                "paymentType": payment_type,
                "service":     service,
                "ebookId":     ebook_id,
                "name":        customer.get("name", ""),
                "email":       customer.get("email", ""),
                "phone":       customer.get("phone", ""),
            },
        })
    except Exception as e:
        logger.error("Razorpay order creation failed: %s", e)
        return JsonResponse({"success": False, "error": str(e)}, status=502)

    # ── Save order to DB ─────────────────────────────────────────────────────
    # Link to logged-in user if present
    user = request.user if request.user.is_authenticated else None

    Order.objects.create(
        razorpay_order_id = rz_order["id"],
        ebook_id          = ebook_id,
        payment_type      = payment_type,
        service           = service,
        customer_name     = customer.get("name", ""),
        customer_email    = customer.get("email", ""),
        customer_phone    = customer.get("phone", ""),
        amount            = expected,
        status            = Order.STATUS_CREATED,
        user              = user,
    )

    logger.info("Order created: %s | %s | ₹%s", rz_order["id"], customer.get("email"), expected)

    return JsonResponse({
        "success":  True,
        "keyId":    settings.RAZORPAY_KEY_ID,
        "orderId":  rz_order["id"],
        "amount":   rz_order["amount"],
        "currency": rz_order["currency"],
    })


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/verify  — Verify client-side payment signature
# ─────────────────────────────────────────────────────────────────────────────
@csrf_exempt
@require_POST
def verify_payment(request):
    try:
        body = json.loads(request.body)
    except ValueError:
        return JsonResponse({"success": False, "error": "Invalid JSON body"}, status=400)

    order_id   = body.get("razorpay_order_id", "")
    payment_id = body.get("razorpay_payment_id", "")
    signature  = body.get("razorpay_signature", "")

    if not all([order_id, payment_id, signature]):
        return JsonResponse({"success": False, "error": "Missing payment details"}, status=400)

    # ── HMAC-SHA256 verification ─────────────────────────────────────────────
    msg = f"{order_id}|{payment_id}".encode()
    secret = settings.RAZORPAY_KEY_SECRET.encode()
    expected_sig = hmac.new(secret, msg, hashlib.sha256).hexdigest()

    if not hmac.compare_digest(expected_sig, signature):
        logger.warning("Invalid payment signature for order %s", order_id)
        return JsonResponse({"success": False, "error": "Invalid payment signature"}, status=400)

    # ── Update order in DB ───────────────────────────────────────────────────
    try:
        order = Order.objects.get(razorpay_order_id=order_id)
        order.razorpay_payment_id = payment_id
        order.razorpay_signature  = signature
        order.status              = Order.STATUS_PAID
        order.paid_at             = datetime.now(timezone.utc)
        order.save()

        PaymentRecord.objects.get_or_create(
            order      = order,
            defaults   = {"payment_id": payment_id, "signature": signature},
        )
    except Order.DoesNotExist:
        logger.error("Order not found during verify: %s", order_id)
        return JsonResponse({"success": False, "error": "Order not found"}, status=404)
    except Exception as e:
        logger.error("DB error during verify: %s", e)
        return JsonResponse({"success": False, "error": str(e)}, status=500)

    logger.info("Payment verified: %s | order %s", payment_id, order_id)

    return JsonResponse({
        "success":   True,
        "verified":  True,
        "message":   "Payment verified",
        "paymentId": payment_id,
    })


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/webhook  — Razorpay server-to-server webhook (order.paid)
# ─────────────────────────────────────────────────────────────────────────────
@csrf_exempt
def webhook(request):
    if request.method != "POST":
        return HttpResponse("Method not allowed", status=405)

    raw_body  = request.body
    signature = request.headers.get("X-Razorpay-Signature", "")

    webhook_secret = getattr(settings, "RAZORPAY_WEBHOOK_SECRET", "")

    # ── Verify webhook signature ─────────────────────────────────────────────
    if webhook_secret:
        expected = hmac.new(
            webhook_secret.encode(), raw_body, hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(expected, signature):
            logger.error("Invalid webhook signature")
            return HttpResponse("Invalid signature", status=401)

    try:
        payload = json.loads(raw_body)
    except ValueError:
        return HttpResponse("Bad payload", status=400)

    event = payload.get("event", "")
    logger.info("Razorpay webhook event: %s", event)

    if event != "order.paid":
        return HttpResponse(f"Ignored: {event}", status=200)

    order_entity   = payload.get("payload", {}).get("order",   {}).get("entity", {})
    payment_entity = payload.get("payload", {}).get("payment", {}).get("entity", {})

    if not order_entity:
        return HttpResponse("Malformed payload", status=400)

    notes          = order_entity.get("notes", {})
    customer_email = notes.get("email") or payment_entity.get("email", "")
    customer_name  = notes.get("name") or "Customer"
    ebook_id       = str(notes.get("ebookId", "")).strip()
    payment_type   = str(notes.get("paymentType", "")).strip()
    rz_order_id    = order_entity.get("id", "")

    logger.info("Webhook order: %s | email: %s | ebookId: %s", rz_order_id, customer_email, ebook_id)

    # ── Mark order paid in DB ─────────────────────────────────────────────────
    try:
        order = Order.objects.get(razorpay_order_id=rz_order_id)
        if order.status != Order.STATUS_PAID:
            order.status  = Order.STATUS_PAID
            order.paid_at = datetime.now(timezone.utc)
            order.save()
    except Order.DoesNotExist:
        logger.warning("Order not in DB yet at webhook: %s", rz_order_id)

    # ── Consultation — no ebook delivery needed ───────────────────────────────
    if payment_type == "consultation":
        logger.info("Consultation payment — no ebook delivery.")
        return HttpResponse("OK", status=200)

    if not customer_email:
        logger.error("No customer email in webhook for order %s", rz_order_id)
        return HttpResponse("No email", status=200)

    # ── Resolve eBook file list ───────────────────────────────────────────────
    if ebook_id in EBOOK_FILES and ebook_id != BONUS_ID:
        ids_to_send = [ebook_id]
    elif ebook_id in COMBO_FILES:
        ids_to_send = list(COMBO_FILES[ebook_id])
    else:
        logger.error("Unknown ebookId in webhook: %s", ebook_id)
        return HttpResponse("Unknown ebookId", status=200)

    # Always include bonus workout guide
    if BONUS_ID not in ids_to_send:
        ids_to_send.append(BONUS_ID)

    # ── Duplicate delivery guard ──────────────────────────────────────────────
    try:
        order = Order.objects.get(razorpay_order_id=rz_order_id)
        if order.ebook_delivered:
            logger.info("eBook already delivered for order %s — skipping", rz_order_id)
            return HttpResponse("Already delivered", status=200)
    except Order.DoesNotExist:
        pass

    # ── Send email ────────────────────────────────────────────────────────────
    try:
        _send_ebook_email(customer_email, customer_name, ids_to_send, ebook_id)
        # Mark delivered
        Order.objects.filter(razorpay_order_id=rz_order_id).update(ebook_delivered=True)
        logger.info("eBook email sent to %s for order %s", customer_email, rz_order_id)
    except Exception as e:
        logger.error("Email delivery failed for order %s: %s", rz_order_id, e)
        # Return 500 so Razorpay retries the webhook
        return HttpResponse("Email error — will retry", status=500)

    return HttpResponse("OK", status=200)


# ─────────────────────────────────────────────────────────────────────────────
# Email helper — tries Resend API first, falls back to Django email backend
# ─────────────────────────────────────────────────────────────────────────────
def _send_ebook_email(to_email, to_name, ebook_ids, purchase_ebook_id):
    """Attach purchased PDFs and send via Resend (or Django email backend)."""
    import base64
    import requests as http_requests
    from email.mime.multipart import MIMEMultipart
    from email.mime.base import MIMEBase
    from email.mime.text import MIMEText
    from email import encoders

    ebooks_dir = settings.EBOOKS_PDF_DIR

    # Build title for subject
    if purchase_ebook_id in COMBO_FILES:
        titles = {
            "complete-kalpaahar-collection":     "Complete KalpAahar Collection",
            "protein-&-energy-collection":        "Protein & Energy Collection",
            "happy-family-nutrition-collection":  "Happy Family Nutrition Collection",
            "gut-&-grain-wellness-collection":    "Gut & Grain Wellness Collection",
        }
        purchase_title = titles.get(purchase_ebook_id, "KalpAahar Collection")
    else:
        purchase_title = purchase_ebook_id.replace("-", " ").title()

    resend_key = getattr(settings, "RESEND_API_KEY", "")

    if resend_key and not resend_key.startswith("your_"):
        # ── Resend API (attachments as base64) ───────────────────────────────
        attachments = []
        for eid in ebook_ids:
            filename = EBOOK_FILES.get(eid)
            if not filename:
                continue
            pdf_path = os.path.join(ebooks_dir, filename)
            if not os.path.exists(pdf_path):
                logger.warning("PDF not found: %s", pdf_path)
                continue
            with open(pdf_path, "rb") as f:
                content_b64 = base64.b64encode(f.read()).decode()
            attachments.append({"filename": filename, "content": content_b64})

        html_body = f"""
        <div style="font-family:Arial,sans-serif;line-height:1.6;color:#222;max-width:600px;margin:auto">
          <h2 style="color:#2E8B57">Hi {to_name},</h2>
          <p>Thank you for your purchase! 🎉</p>
          <p>Your <strong>{purchase_title}</strong> is attached to this email.</p>
          <p>🎁 We've also included your <strong>free Move Well Home Workout Guide</strong> as a bonus.</p>
          <p>We hope these resources support your health journey.</p>
          <p>Warm regards,<br><strong>Dr. Sayali Nahar</strong><br>KalpAahar</p>
        </div>
        """

        payload = {
            "from":        settings.EMAIL_FROM,
            "to":          [to_email],
            "subject":     f"Your {purchase_title} is here 🎉",
            "html":        html_body,
            "attachments": attachments,
        }

        resp = http_requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {resend_key}",
                "Content-Type":  "application/json",
            },
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()
        logger.info("Resend response: %s", resp.json())

    else:
        # ── Django email backend fallback (console / SMTP) ───────────────────
        from django.core.mail import EmailMessage

        msg = EmailMessage(
            subject     = f"Your {purchase_title} is here 🎉",
            body        = (
                f"Hi {to_name},\n\n"
                f"Thank you for purchasing {purchase_title}!\n"
                "Please find your eBook(s) attached.\n\n"
                "We've also included a free Move Well Home Workout Guide as a bonus.\n\n"
                "Warm regards,\nDr. Sayali Nahar\nKalpAahar"
            ),
            from_email  = settings.EMAIL_FROM,
            to          = [to_email],
        )

        for eid in ebook_ids:
            filename = EBOOK_FILES.get(eid)
            if not filename:
                continue
            pdf_path = os.path.join(ebooks_dir, filename)
            if not os.path.exists(pdf_path):
                logger.warning("PDF not found: %s", pdf_path)
                continue
            with open(pdf_path, "rb") as f:
                msg.attach(filename, f.read(), "application/pdf")

        msg.send()
