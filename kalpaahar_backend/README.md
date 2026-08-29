# KalpAahar Django Backend

## Quick Start
cd kalpaahar_backend
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_ebooks
python manage.py runserver 8000

Open: http://127.0.0.1:8000

## Admin
URL:      http://127.0.0.1:8000/admin/
Login:    admin@kalpaahar.in
Password: Admin@1234  (change after first login)

## Auth Pages
Register: http://127.0.0.1:8000/auth/register/
Login:    http://127.0.0.1:8000/auth/login/

## API Endpoints
POST /api/orders       - Create Razorpay order
POST /api/verify       - Verify payment signature
POST /api/webhook      - Razorpay webhook (order.paid -> email PDF)
GET  /api/auth-status  - Check login state (used by frontend nav)

## Razorpay (live)
RAZORPAY_KEY_ID         = rzp_live_TVFc8rCKqgU8r9
RAZORPAY_KEY_SECRET     = JELuztPRo7xDfWuaiiVGwnSh
RAZORPAY_WEBHOOK_SECRET = Kalpaahar_Razorpay_Webhook_2026_X9!mP7#qL2

## Webhook Setup (Razorpay Dashboard)
URL:    https://yourdomain.com/api/webhook
Secret: Kalpaahar_Razorpay_Webhook_2026_X9!mP7#qL2
Event:  order.paid

For local testing: ngrok http 8000 -> use https ngrok URL/api/webhook