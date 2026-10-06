from django.urls import path
from .api_views import OrderListCreateView, OrderDetailView

app_name = 'orders_api'

urlpatterns = [
    path('', OrderListCreateView.as_view(), name='order-list'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
]