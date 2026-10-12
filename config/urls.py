from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from cart import views

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("", include("home.urls")),
    path("products/", include("products.urls")),
    path("users/", include("users.urls")),
    path("cart/", include("cart.urls")),
    path("orders/", include("orders.urls")),
    path("payments/", include("payments.urls")),
    path("admin/", include("admin_dashboard.urls")),
    re_path(
        r"^dashboard/(?P<path>.*)$",
        RedirectView.as_view(url="/admin/%(path)s", permanent=True),
    ),
    path("wishlist/", views.wishlist, name="wishlist"),
    path("wishlist/api/", include("cart.wishlist_api_urls")),
]


# Serve uploaded media files locally in debug mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
