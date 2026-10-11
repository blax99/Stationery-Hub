from types import SimpleNamespace

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.test import RequestFactory, SimpleTestCase, TestCase
from django.urls import resolve

from .views import (
    analytics_view,
    admin_required,
    dashboard_view,
    inventory_view,
    orders_view,
    products_view,
    users_view,
)


class DashboardIntegrationTests(SimpleTestCase):
    dashboard_routes = {
        "/dashboard/": dashboard_view,
        "/dashboard/products/": products_view,
        "/dashboard/inventory/": inventory_view,
        "/dashboard/orders/": orders_view,
        "/dashboard/analytics/": analytics_view,
        "/dashboard/users/": users_view,
    }

    def setUp(self):
        self.factory = RequestFactory()

    def test_dashboard_routes_resolve_to_their_modules(self):
        for path, view in self.dashboard_routes.items():
            with self.subTest(path=path):
                self.assertIs(resolve(path).func, view)

    def test_all_modules_render_the_same_navigation_without_extra_groups(self):
        pages = {
            "dashboard.html": "dashboard",
            "products.html": "products",
            "inventory.html": "inventory",
            "orders.html": "orders",
            "analytics.html": "analytics",
            "users.html": "users",
        }
        for template_name, active_page in pages.items():
            with self.subTest(template=template_name):
                html = render_to_string(
                    f"admin_dashboard/{template_name}",
                    {"active_page": active_page},
                )
                self.assertEqual(html.count('aria-label="Admin dashboard"'), 1)
                for label in (
                    "Dashboard",
                    "Products",
                    "Inventory",
                    "Orders",
                    "Analytics",
                    "Users",
                ):
                    self.assertIn(label, html)
                self.assertNotIn(">Management<", html)
                self.assertIn('aria-current="page"', html)
                self.assertIn("Stationery Hub - Admin", html)

    def test_all_admin_pages_use_stationery_hub_title_and_favicon(self):
        pages = (
            "dashboard.html",
            "products.html",
            "inventory.html",
            "orders.html",
            "analytics.html",
            "users.html",
        )
        for template_name in pages:
            with self.subTest(template=template_name):
                html = render_to_string(
                    f"admin_dashboard/{template_name}",
                    {"active_page": template_name.removesuffix(".html")},
                )
                self.assertIn("<title>Stationery Hub - Admin</title>", html)
                self.assertIn(
                    '<link rel="icon" href="https://img.icons8.com/clouds/100/stationery.png" />',
                    html,
                )

    def test_dashboard_and_analytics_use_orders_page_heading_style(self):
        dashboard_html = render_to_string("admin_dashboard/dashboard.html")
        analytics_html = render_to_string("admin_dashboard/analytics.html")

        for html, title in (
            (dashboard_html, "Dashboard"),
            (analytics_html, "Analytics"),
        ):
            with self.subTest(title=title):
                self.assertIn('class="flex-1 p-8"', html)
                self.assertIn('class="mb-8', html)
                self.assertIn('class="text-3xl font-bold text-gray-800"', html)
                self.assertIn(f">{title}</h2>", html)

        self.assertNotIn("Stationery Hub management panel", dashboard_html)
        self.assertNotIn("Admin ▼", dashboard_html)

    def test_dashboard_modules_require_authentication(self):
        for path, view in self.dashboard_routes.items():
            request = self.factory.get(path)
            request.user = AnonymousUser()

            with self.subTest(path=path):
                response = view(request)
                self.assertEqual(response.status_code, 302)
                self.assertIn("/users/login-page/", response.url)

    def test_dashboard_modules_reject_non_admin_users(self):
        for path, view in self.dashboard_routes.items():
            request = self.factory.get(path)
            request.user = SimpleNamespace(
                is_authenticated=True, role="customer", is_superuser=False
            )

            with self.subTest(path=path):
                with self.assertRaises(PermissionDenied):
                    view(request)

    def test_superusers_are_allowed_to_access_the_dashboard(self):
        request = self.factory.get("/dashboard/")
        request.user = SimpleNamespace(
            is_authenticated=True, role="customer", is_superuser=True
        )

        protected_view = admin_required(lambda request: HttpResponse("allowed"))
        response = protected_view(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"allowed")


class DashboardUserRoleTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.admin = user_model.objects.create_user(
            username="dashboard-admin",
            email="dashboard-admin@example.com",
            password="TestPass123",
            role="admin",
        )
        self.customer = user_model.objects.create_user(
            username="dashboard-customer",
            email="dashboard-customer@example.com",
            password="TestPass123",
            role="customer",
        )
        self.vendor = user_model.objects.create_user(
            username="dashboard-vendor",
            email="dashboard-vendor@example.com",
            password="TestPass123",
            role="vendor",
        )
        self.client.force_login(self.admin)

    def test_user_module_lists_only_admins_and_customers(self):
        response = self.client.get("/dashboard/users/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.admin.email)
        self.assertContains(response, self.customer.email)
        self.assertNotContains(response, self.vendor.email)
        self.assertNotContains(response, 'value="vendor"')
        self.assertNotContains(response, "Vendor")

    def test_user_module_rejects_vendor_role_on_add(self):
        response = self.client.post(
            "/dashboard/users/",
            {
                "action": "add",
                "full_name": "New Vendor",
                "email": "new-vendor@example.com",
                "password": "TestPass123",
                "role": "vendor",
            },
            follow=True,
        )

        self.assertFalse(
            get_user_model().objects.filter(email="new-vendor@example.com").exists()
        )
        self.assertContains(response, "Choose either Admin or Customer.")

    def test_user_module_rejects_vendor_role_on_edit(self):
        response = self.client.post(
            "/dashboard/users/",
            {
                "action": "edit",
                "user_id": self.customer.id,
                "full_name": "Dashboard Customer",
                "email": self.customer.email,
                "role": "vendor",
            },
            follow=True,
        )

        self.customer.refresh_from_db()
        self.assertEqual(self.customer.role, "customer")
        self.assertContains(response, "Choose either Admin or Customer.")
