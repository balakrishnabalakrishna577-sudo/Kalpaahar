from django.db import models


class Ebook(models.Model):
    ebook_id    = models.CharField(max_length=100, unique=True, help_text="Slug used in Razorpay notes, e.g. 'gut-reset'")
    title       = models.CharField(max_length=200)
    price       = models.IntegerField(help_text="Price in INR")
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to="ebook_covers/", blank=True)
    pdf_file    = models.FileField(upload_to="ebooks/",        blank=True)
    is_active   = models.BooleanField(default=True)
    is_combo    = models.BooleanField(default=False)
    combo_items = models.ManyToManyField(
        "self",
        blank=True,
        symmetrical=False,
        related_name="part_of_combos",
        help_text="For combo packs: individual eBooks included in this combo",
    )
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering            = ["is_combo", "title"]
        verbose_name        = "eBook"
        verbose_name_plural = "eBooks"

    def __str__(self):
        return f"{self.title} — ₹{self.price}"
