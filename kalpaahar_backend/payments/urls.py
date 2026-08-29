from django.urls import path
from . import views

urlpatterns = [
    path("orders",  views.create_order,   name="api_orders"),
    path("verify",  views.verify_payment, name="api_verify"),
    path("webhook", views.webhook,        name="api_webhook"),
]
