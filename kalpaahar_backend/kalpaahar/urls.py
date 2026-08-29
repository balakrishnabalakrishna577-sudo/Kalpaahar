from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse, FileResponse
from django.views.generic import TemplateView
from accounts.views import auth_status as auth_status_view
import os

admin.site.site_header = "KalpAahar Admin"
admin.site.site_title  = "KalpAahar"
admin.site.index_title = "Dashboard"


def serve_frontend(request):
    index_path = os.path.join(settings.FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(open(index_path, "rb"), content_type="text/html")
    return HttpResponse("<h1>index.html not found</h1>", status=404)


def serve_frontend_file(request, filename):
    file_path = os.path.join(settings.FRONTEND_DIR, filename)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(open(file_path, "rb"))
    from django.http import Http404
    raise Http404


urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include("accounts.urls")),
    path("api/auth-status", auth_status_view, name="api_auth_status"),
    path("api/", include("payments.urls")),
    path("checkout/success/", TemplateView.as_view(template_name="checkout/success.html"), name="checkout_success"),
    path("", serve_frontend, name="home"),
    path("<path:filename>", serve_frontend_file, name="frontend_file"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
