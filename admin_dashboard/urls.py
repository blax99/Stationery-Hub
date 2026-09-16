from django.urls import path
from .views import dashboard_view, products_view, inventory_view, orders_view, analytics_view

urlpatterns = [
    path("", dashboard_view, name="dashboard"),
    path("products/", products_view, name="products"),
    path("inventory/", inventory_view, name="inventory"),
    path("orders/", orders_view, name="orders"),
    path("analytics/", analytics_view, name="analytics"),
    
]