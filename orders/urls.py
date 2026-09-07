from django.urls import path
from . import views

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path(
    'order-confirmation/<int:order_id>/',
    views.checkout_confirmation,
    name='order_confirmation'
),
]
