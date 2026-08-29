"""
Management command: python manage.py seed_ebooks

Creates or updates all eBook and combo records in the database.
Safe to run multiple times (uses update_or_create).
"""
from django.core.management.base import BaseCommand
from ebooks.models import Ebook


INDIVIDUAL_EBOOKS = [
    {
        "ebook_id":    "high-protein-breakfast",
        "title":       "High Protein Breakfast",
        "price":       299,
        "description": "Start your day strong with 30+ high-protein breakfast recipes crafted by Dr. Sayali Nahar.",
    },
    {
        "ebook_id":    "gut-reset",
        "title":       "Gut Health Reset",
        "price":       299,
        "description": "A science-backed guide to healing your gut with food — recipes, meal plans, and lifestyle tips.",
    },
    {
        "ebook_id":    "power-lunch",
        "title":       "Power Lunch",
        "price":       299,
        "description": "Energising midday meals that keep you focused and fuelled through the afternoon.",
    },
    {
        "ebook_id":    "snack-smart",
        "title":       "Snack Smart",
        "price":       299,
        "description": "Healthy, satisfying snacks that curb cravings without derailing your nutrition goals.",
    },
    {
        "ebook_id":    "ancient-grain-modern-plate",
        "title":       "Ancient Grain, Modern Plate",
        "price":       299,
        "description": "Rediscover millets, sorghum, and ancient Indian grains in contemporary everyday recipes.",
    },
    {
        "ebook_id":    "picky-eaters",
        "title":       "Picky Eaters",
        "price":       299,
        "description": "Practical strategies and child-friendly recipes to get fussy kids excited about nutritious food.",
    },
]

COMBO_EBOOKS = [
    {
        "ebook_id":    "complete-kalpaahar-collection",
        "title":       "Complete KalpAahar Collection",
        "price":       1299,
        "description": "All 6 KalpAahar eBooks in one bundle — the complete nutrition library.",
        "combo_ids":   [
            "high-protein-breakfast", "gut-reset", "power-lunch",
            "snack-smart", "ancient-grain-modern-plate", "picky-eaters",
        ],
    },
    {
        "ebook_id":    "protein-&-energy-collection",
        "title":       "Protein & Energy Collection",
        "price":       699,
        "description": "High Protein Breakfast + Power Lunch + Snack Smart — your complete energy toolkit.",
        "combo_ids":   ["high-protein-breakfast", "power-lunch", "snack-smart"],
    },
    {
        "ebook_id":    "happy-family-nutrition-collection",
        "title":       "Happy Family Nutrition Collection",
        "price":       699,
        "description": "Picky Eaters + High Protein Breakfast + Snack Smart — feed the whole family well.",
        "combo_ids":   ["picky-eaters", "high-protein-breakfast", "snack-smart"],
    },
    {
        "ebook_id":    "gut-&-grain-wellness-collection",
        "title":       "Gut & Grain Wellness Collection",
        "price":       749,
        "description": "Gut Health Reset + Ancient Grain, Modern Plate + High Protein Breakfast.",
        "combo_ids":   ["gut-reset", "ancient-grain-modern-plate", "high-protein-breakfast"],
    },
]


class Command(BaseCommand):
    help = "Seed the database with all KalpAahar eBook catalog entries"

    def handle(self, *args, **options):
        self.stdout.write("Seeding individual eBooks...")
        for data in INDIVIDUAL_EBOOKS:
            obj, created = Ebook.objects.update_or_create(
                ebook_id=data["ebook_id"],
                defaults={
                    "title":       data["title"],
                    "price":       data["price"],
                    "description": data["description"],
                    "is_active":   True,
                    "is_combo":    False,
                },
            )
            status = "Created" if created else "Updated"
            self.stdout.write(f"  {status}: {obj.title}")

        self.stdout.write("Seeding combo packs...")
        for data in COMBO_EBOOKS:
            obj, created = Ebook.objects.update_or_create(
                ebook_id=data["ebook_id"],
                defaults={
                    "title":       data["title"],
                    "price":       data["price"],
                    "description": data["description"],
                    "is_active":   True,
                    "is_combo":    True,
                },
            )
            # Set M2M combo items
            combo_qs = Ebook.objects.filter(ebook_id__in=data["combo_ids"])
            obj.combo_items.set(combo_qs)
            status = "Created" if created else "Updated"
            self.stdout.write(f"  {status}: {obj.title} ({combo_qs.count()} items)")

        total = Ebook.objects.count()
        self.stdout.write(self.style.SUCCESS(f"\nDone! {total} eBook records in database."))
