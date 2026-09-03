import requests
from django.conf import settings
from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response

from orders.models import Order
from .models import KhaltiTransaction


@api_view(['POST'])
def initiate_khalti_payment(request):
    order_id = request.data.get('order_id')
    order = get_object_or_404(Order, id=order_id)

    amount_paisa = int(order.total_amount * 100)  # convert NPR to paisa

    url = f"{settings.KHALTI_BASE_URL}/epayment/initiate/"
    headers = {"Authorization": f"key {settings.KHALTI_SECRET_KEY}"}
    payload = {
        "return_url": settings.KHALTI_RETURN_URL,
        "website_url": settings.KHALTI_WEBSITE_URL,
        "amount": amount_paisa,
        "purchase_order_id": str(order.id),
        "purchase_order_name": order.order_name,
        "customer_info": {
            "name": order.user.get_full_name() or order.user.username,
            "email": order.user.email,
            "phone": getattr(order.user, 'phone', '9800000001'),
        }
    }

    res = requests.post(url, json=payload, headers=headers)
    data = res.json()

    if res.status_code == 200:
        KhaltiTransaction.objects.create(
            order=order,
            pidx=data.get('pidx'),
            amount_paisa=amount_paisa,
            status='Initiated'
        )
        return Response({"payment_url": data.get('payment_url'), "pidx": data.get('pidx')})

    return Response(data, status=res.status_code)


@api_view(['GET'])
def verify_khalti_payment(request):
    pidx = request.GET.get('pidx')
    txn = get_object_or_404(KhaltiTransaction, pidx=pidx)

    url = f"{settings.KHALTI_BASE_URL}/epayment/lookup/"
    headers = {"Authorization": f"key {settings.KHALTI_SECRET_KEY}"}
    res = requests.post(url, json={"pidx": pidx}, headers=headers)
    data = res.json()

    status = data.get('status')
    txn.status = status
    txn.verified_at = timezone.now()
    txn.save()

    if status == 'Completed':
        txn.order.status = 'paid'
        txn.order.save()
        return redirect('/orders/success/')
    elif status in ['Expired', 'User canceled']:
        txn.order.status = 'failed'
        txn.order.save()
        return redirect('/orders/failed/')
    else:
        # Pending or unknown — don't finalize, ask user to retry lookup
        return redirect('/orders/pending/')