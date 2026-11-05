from types import SimpleNamespace

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.test import RequestFactory, SimpleTestCase, TestCase
from django.urls import resolve, reverse

from orders.models import Order
from products.models import Category, Products

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
        "/admin/": dashboard_view,
        "/admin/products/": products_view,
        "/admin/inventory/": inventory_view,
        "/admin/orders/": orders_view,
        "/admin/analytics/": analytics_view,
        "/admin/users/": users_view,
    }

    def setUp(self):
        self.factory = RequestFactory()

    def test_dashboard_routes_resolve_to_their_modules(self):
        for path, view in self.dashboard_routes.items():
            with self.subTest(path=path):
                self.assertIs(resolve(path).func, view)

    def test_legacy_dashboard_urls_redirect_to_admin_urls(self):
        for path in ("/dashboard/", "/dashboard/products/"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 301)
                self.assertEqual(
                    response["Location"],
                    path.replace("/dashboard/", "/admin/"),
                )

    def test_django_admin_is_available_at_its_new_url(self):
        self.assertEqual(reverse("admin:index"), "/django-admin/")

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
                self.assertIn('href="/"', html)
                self.assertIn("View website", html)
                self.assertIn('id="adminLogoutButton"', html)
                self.assertIn("Sign out", html)
                self.assertIn("Admin logout successful.", html)
                self.assertIn("right: 1rem", html)
                self.assertIn('id="adminSidebarToggle"', html)
                self.assertIn('aria-controls="adminSidebarContent"', html)
                self.assertIn('aria-expanded="false"', html)
                self.assertIn('data-menu-icon="open"', html)
                self.assertIn('data-menu-icon="close" class="hidden', html)
                self.assertIn("willExpand ? \"Close admin navigation\"", html)
                self.assertIn('id="adminSidebarContent"', html)
                self.assertIn("md:sticky", html)
                self.assertIn("md:h-screen", html)
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

    def test_admin_pages_use_in_page_confirmation_instead_of_browser_prompts(self):
        pages = (
            "users.html",
            "products.html",
            "inventory.html",
            "orders.html",
        )
        for template_name in pages:
            with self.subTest(template=template_name):
                html = render_to_string(
                    f"admin_dashboard/{template_name}",
                    {"active_page": template_name.removesuffix(".html")},
                )
                self.assertIn('id="adminConfirmationModal"', html)
                self.assertIn("window.showAdminConfirmation", html)
                self.assertNotIn("confirm(", html)
                self.assertNotIn("prompt(", html)

    def test_dashboard_and_analytics_use_orders_page_heading_style(self):
        dashboard_html = render_to_string("admin_dashboard/dashboard.html")
        analytics_html = render_to_string("admin_dashboard/analytics.html")

        for html, title in (
            (dashboard_html, "Dashboard"),
            (analytics_html, "Analytics"),
        ):
            with self.subTest(title=title):
                self.assertIn('class="min-w-0 flex-1 p-4 sm:p-6 lg:p-8"', html)
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
        request = self.factory.get("/admin/")
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
        response = self.client.get("/admin/users/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.admin.email)
        self.assertContains(response, self.customer.email)
        self.assertNotContains(response, self.vendor.email)
        self.assertNotContains(response, 'value="vendor"')
        self.assertNotContains(response, "Vendor")

    def test_admin_can_sign_out_and_is_redirected_from_dashboard(self):
        response = self.client.post("/users/logout/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"success": True})
        self.assertRedirects(
            self.client.get("/admin/"),
            "/users/login-page/?next=/admin/",
            fetch_redirect_response=False,
        )

    def test_user_module_rejects_vendor_role_on_add(self):
        response = self.client.post(
            "/admin/users/",
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

    def test_user_module_notifies_when_admin_or_customer_account_is_created(self):
        for role, message in (
            ("admin", "Admin account created successfully."),
            ("customer", "User account created successfully."),
        ):
            with self.subTest(role=role):
                email = f"new-{role}@example.com"
                response = self.client.post(
                    "/admin/users/",
                    {
                        "action": "add",
                        "full_name": "New Account",
                        "email": email,
                        "password": "TestPass123",
                        "role": role,
                    },
                    follow=True,
                )

                self.assertContains(response, message)
                self.assertContains(
                    response,
                    'data-admin-notification="success"',
                )
                self.assertTrue(get_user_model().objects.filter(email=email).exists())

    def test_user_module_rejects_vendor_role_on_edit(self):
        response = self.client.post(
            "/admin/users/",
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

    def test_cancelled_orders_are_counted_and_displayed_in_admin_pages(self):
        Order.objects.create(
            user=self.customer,
            total_amount="25.00",
            status="cancelled",
        )

        dashboard_response = self.client.get("/admin/")
        orders_response = self.client.get("/admin/orders/")
        analytics_response = self.client.get("/admin/analytics/")

        self.assertEqual(dashboard_response.context["cancelled_orders"], 1)
        self.assertContains(dashboard_response, "bg-red-100 text-red-700")
        self.assertContains(orders_response, 'data-status="cancelled"')
        self.assertEqual(orders_response.context["cancelled_orders"], 1)
        self.assertContains(orders_response, "bg-red-100 text-red-700")
        self.assertContains(orders_response, '<option value="cancelled"')
        self.assertEqual(analytics_response.context["cancelled_orders"], 1)

    def test_dashboard_customer_count_includes_only_customer_role(self):
        response = self.client.get("/admin/")

        self.assertEqual(response.context["total_customers"], 1)
        self.assertContains(response, "Customers")

    def test_user_search_is_filtered_and_paginated(self):
        for index in range(26):
            get_user_model().objects.create_user(
                username=f"pagination-customer-{index}",
                email=f"pagination-customer-{index}@example.com",
                password="TestPass123",
                role="customer",
            )

        response = self.client.get(
            "/admin/users/?q=pagination-customer&role=customer"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["page_obj"].paginator.count, 26)
        self.assertEqual(response.context["page_obj"].paginator.per_page, 10)
        self.assertEqual(len(response.context["users"]), 10)
        self.assertContains(response, "Page 1 of 3")
        self.assertContains(response, "role=customer")

        response = self.client.get(
            "/admin/users/?q=pagination-customer&role=customer&page=2"
        )

        self.assertEqual(response.context["page_obj"].number, 2)
        self.assertEqual(len(response.context["users"]), 10)

    def test_product_and_inventory_lists_are_paginated_and_filtered(self):
        category = Category.objects.create(name="Pagination supplies")
        for index in range(26):
            Products.objects.create(
                category=category,
                name=f"Pagination product {index}",
                description="Admin list pagination test",
                price="5.00",
                stock=index % 12,
            )

        products_response = self.client.get(
            f"/admin/products/?q=Pagination&category={category.id}"
        )
        inventory_response = self.client.get(
            "/admin/inventory/?q=Pagination&status=low_stock"
        )

        self.assertEqual(products_response.status_code, 200)
        self.assertEqual(products_response.context["page_obj"].paginator.count, 26)
        self.assertEqual(products_response.context["page_obj"].paginator.per_page, 10)
        self.assertEqual(len(products_response.context["products"]), 10)
        self.assertContains(products_response, "Page 1 of 3")

        self.assertEqual(inventory_response.status_code, 200)
        self.assertEqual(inventory_response.context["page_obj"].paginator.count, 21)
        self.assertEqual(len(inventory_response.context["products"]), 10)
        self.assertTrue(
            all(
                0 < product.stock <= 10
                for product in inventory_response.context["products"]
            )
        )

    def test_order_list_is_paginated_and_searchable(self):
        for index in range(26):
            Order.objects.create(
                user=self.customer,
                total_amount="25.00",
                status="pending",
            )

        response = self.client.get(
            f"/admin/orders/?q={self.customer.username}&status=pending"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["page_obj"].paginator.count, 26)
        self.assertEqual(response.context["page_obj"].paginator.per_page, 10)
        self.assertEqual(len(response.context["orders"]), 10)
        self.assertContains(response, "Page 1 of 3")
