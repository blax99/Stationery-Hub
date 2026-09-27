from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from datetime import timedelta
from .models import Order, ShippingAddress


@login_required
def checkout(request):
    if request.method == "POST":
        order = Order.objects.create(
            user=request.user,
            total_amount=0.00
        )

        ShippingAddress.objects.create(
            order=order,
            full_name=request.POST.get("full_name"),
            address=request.POST.get("address"),
            city=request.POST.get("city"),
            phone=request.POST.get("phone")
        )

        return redirect(
            'order_confirmation',
            order_id=order.id
        )

    return render(request, 'checkout.html')


@login_required
def checkout_confirmation(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    estimated_delivery_start = order.created_at + timedelta(days=3)
    estimated_delivery_end = order.created_at + timedelta(days=5)

    return render(
        request,
        'order/confirmation.html',
        {
            'order': order,
            'estimated_delivery_start': estimated_delivery_start,
            'estimated_delivery_end': estimated_delivery_end,
        }
    )


@login_required
def order_history(request):
    orders = Order.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(
        request,
        'order/history.html',
        {'orders': orders}
    )


@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    if request.method == "POST":
        if order.status in ['pending', 'confirmed']:
            order.status = 'cancelled'
            order.save()

    return redirect('order_history')


@login_required
def request_return(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    if request.method == "POST":
        if order.status == 'delivered':
            order.status = 'return_requested'
            order.save()

    return redirect('order_history')