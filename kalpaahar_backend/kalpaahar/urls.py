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
        response = FileResponse(open(index_path, "rb"), content_type="text/html; charset=utf-8")
        # Never cache index.html - always serve fresh JS fixes
        response["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response["Pragma"]        = "no-cache"
        response["Expires"]       = "0"
        return response
    return HttpResponse("<h1>index.html not found</h1>", status=404)


def serve_frontend_file(request, filename):
    # Security: prevent path traversal
    safe_path = os.path.normpath(os.path.join(settings.FRONTEND_DIR, filename))
    if not safe_path.startswith(str(settings.FRONTEND_DIR)):
        from django.http import Http404
        raise Http404
    if os.path.exists(safe_path) and os.path.isfile(safe_path):
        response = FileResponse(open(safe_path, "rb"))
        # Cache static assets (images, PDFs) for 1 hour
        response["Cache-Control"] = "public, max-age=3600"
        return response
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
