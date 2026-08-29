from django.contrib import admin
from django.utils.html import format_html
from .models import Ebook


@admin.register(Ebook)
class EbookAdmin(admin.ModelAdmin):
    list_display   = ["title", "ebook_id", "price_display", "is_active", "is_combo", "cover_preview"]
    list_filter    = ["is_active", "is_combo"]
    search_fields  = ["title", "ebook_id"]
    ordering       = ["is_combo", "title"]
    filter_horizontal = ["combo_items"]

    fieldsets = (
        ("Details",     {"fields": ("ebook_id", "title", "price", "description", "is_active", "is_combo")}),
        ("Files",       {"fields": ("cover_image", "pdf_file")}),
        ("Combo items", {"fields": ("combo_items",), "classes": ("collapse",)}),
    )

    def price_display(self, obj):
        return f"₹{obj.price}"
    price_display.short_description = "Price"

    def cover_preview(self, obj):
        if obj.cover_image:
            return format_html(
                '<img src="{}" style="height:48px;border-radius:6px;object-fit:cover;" />',
                obj.cover_image.url,
            )
        return "—"
    cover_preview.short_description = "Cover"
