from django.urls import path
from . import views


urlpatterns = [
    path(
        'checkout/',
        views.checkout,
        name='checkout'
    ),

    path(
        'order-confirmation/<int:order_id>/',
        views.checkout_confirmation,
        name='order_confirmation'
    ),

    path(
        'order-history/',
        views.order_history,
        name='order_history'
    ),

    path(
        'order/<int:order_id>/cancel/',
        views.cancel_order,
        name='cancel_order'
    ),

    path(
        'order/<int:order_id>/return/',
        views.request_return,
        name='request_return'
    ),
]
