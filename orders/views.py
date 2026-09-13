from django.shortcuts import render, get_object_or_404
from .models import Order

def checkout(request):
    return render(request, 'checkout.html')

def checkout_confirmation(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    return render(
        request,
        'order/confirmation.html',
        {'order': order}
    )