import importlib

from django.apps import apps
from django.db import connection
from django.test import TestCase
from django.urls import reverse

from .models import Category, Products


class ProductDetailTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Writing")
        self.product = Products.objects.create(
            category=self.category,
            name="Test pen",
            description="A smooth-writing pen.",
            price="12.50",
            stock=3,
        )

    def test_product_detail_shows_saved_description(self):
        response = self.client.get(
            reverse("products:product_detail", args=[self.product.slug])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A smooth-writing pen.")
        self.assertNotContains(
            response, "No description provided for this product."
        )

    def test_product_detail_shows_fallback_when_description_is_empty(self):
        self.product.description = ""
        self.product.save(update_fields=["description"])

        response = self.client.get(
            reverse("products:product_detail", args=[self.product.slug])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No description provided for this product.")


class ProductListPaginationTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Writing")
        self.products = [
            Products.objects.create(
                category=self.category,
                name=f"Test pen {number}",
                description="A smooth-writing pen.",
                price="12.50",
                stock=3,
            )
            for number in range(8)
        ]

    def test_product_list_shows_six_products_per_page(self):
        response = self.client.get(reverse("products:product_list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["products"]), 6)
        self.assertEqual(response.context["page_obj"].paginator.count, 8)
        self.assertContains(response, "page=2")

    def test_product_list_paginates_and_preserves_query_filters(self):
        response = self.client.get(
            reverse("products:product_list_by_category", args=[self.category.slug]),
            {"page": 2, "sort": "price_low", "q": "pen"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["products"]), 2)
        self.assertContains(response, "?sort=price_low&amp;q=pen&amp;page=1")
        self.assertContains(response, "?sort=price_low&amp;q=pen&amp;page=2")


class CategoryDataMigrationTests(TestCase):
    def test_old_pencil_products_move_to_pens_and_sports_is_added(self):
        pens = Category.objects.get(name="Pens")
        pencils, _ = Category.objects.get_or_create(name="Pencils and Lead")
        product = Products.objects.create(
            category=pencils,
            name="Test pencil",
            description="A test pencil.",
            price="2.50",
            stock=4,
        )

        migration = importlib.import_module(
            "products.migrations.0004_merge_pencils_lead_into_pens_add_sports"
        )
        with connection.schema_editor() as schema_editor:
            migration.update_categories(apps, schema_editor)

        product.refresh_from_db()
        self.assertEqual(product.category_id, pens.id)
        self.assertFalse(Category.objects.filter(pk=pencils.pk).exists())
        self.assertTrue(Category.objects.filter(name="Sports", slug="sports").exists())
