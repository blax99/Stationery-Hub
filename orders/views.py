from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from datetime import timedelta
from .models import Order, OrderItem, ShippingAddress
from cart.models import Cart


@login_required
def checkout(request):
    cart = Cart.objects.filter(user=request.user).first()
    cart_items = list(
        cart.items.select_related('product') if cart else []
    )

    for item in cart_items:
        item.line_total = item.product.price * item.quantity

    total_amount = sum(
        (item.line_total for item in cart_items),
        start=0
    )

    if request.method == "POST":
        if not cart_items:
            return redirect('cart')

        order = Order.objects.create(
            user=request.user,
            total_amount=total_amount
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product_name=item.product.name,
                quantity=item.quantity,
                price=item.product.price
            )

        ShippingAddress.objects.create(
            order=order,
            full_name=request.POST.get("full_name"),
            address=request.POST.get("address"),
            city=request.POST.get("city"),
            phone=request.POST.get("phone")
        )

        cart.items.all().delete()

        return redirect(
            'order_confirmation',
            order_id=order.id
        )

    return render(
        request,
        'checkout.html',
        {
            'cart_items': cart_items,
            'total_amount': total_amount,
            'email': request.user.email,
            'phone_number': request.user.phone_number,
        }
    )


@login_required
@ensure_csrf_cookie
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
    if request.method != "POST":
        return redirect('order_history')

    from payments.models import ACTIVE_TRANSACTION_TIMEOUT, KhaltiTransaction

    with transaction.atomic():
        order = get_object_or_404(
            Order.objects.select_for_update(),
            id=order_id,
            user=request.user
        )

        if order.payment_status == 'paid':
            cancellation_result = 'paid'
        elif order.status not in ('pending', 'confirmed'):
            cancellation_result = 'unavailable'
        else:
            now = timezone.now()
            KhaltiTransaction.objects.filter(
                order=order,
                status__in=('Initiated', 'Pending'),
                created_at__lt=now - ACTIVE_TRANSACTION_TIMEOUT,
            ).update(status='Expired')

            payment_in_progress = KhaltiTransaction.objects.filter(
                order=order,
                status__in=('Initiated', 'Pending'),
                created_at__gte=now - ACTIVE_TRANSACTION_TIMEOUT,
            ).exists()

            if payment_in_progress:
                cancellation_result = 'payment_in_progress'
            else:
                order.status = 'cancelled'
                order.save(update_fields=['status', 'updated_at'])
                cancellation_result = None

    if cancellation_result:
        return redirect(
            f"{reverse('order_confirmation', args=[order.id])}"
            f"?cancellation={cancellation_result}"
        )
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
