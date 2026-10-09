import logging
from urllib.parse import urlsplit, urlunsplit

import requests
from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from orders.models import Order
from .models import ACTIVE_TRANSACTION_TIMEOUT, KhaltiTransaction


logger = logging.getLogger(__name__)


def _expire_payment_attempt(payment_attempt):
    KhaltiTransaction.objects.filter(
        pk=payment_attempt.pk,
        status__in=('Initiated', 'Pending'),
    ).update(status='Expired')


def _get_khalti_return_url():
    configured_url = urlsplit(settings.KHALTI_RETURN_URL)
    if (
        configured_url.scheme not in ('http', 'https')
        or not configured_url.netloc
    ):
        raise ValueError('KHALTI_RETURN_URL must be an absolute HTTP(S) URL.')

    return urlunsplit((
        configured_url.scheme,
        configured_url.netloc,
        reverse('khalti-verify'),
        '',
        '',
    ))


def _gateway_error(data, http_status):
    if isinstance(data, dict):
        detail = data.get('detail') or data.get('error')
        if detail:
            return str(detail)

        errors = data.get('errors')
        if isinstance(errors, dict):
            messages = [
                f'{field}: {", ".join(map(str, messages))}'
                for field, messages in errors.items()
                if isinstance(messages, list)
            ]
            if messages:
                return ' '.join(messages)

        validation_messages = [
            f'{field}: {", ".join(map(str, messages))}'
            for field, messages in data.items()
            if field != 'error_key' and isinstance(messages, list)
        ]
        if validation_messages:
            return ' '.join(validation_messages)

        error_key = data.get('error_key')
        if error_key:
            return f'Khalti rejected the payment request ({error_key}).'

    return f'Khalti rejected the payment request (HTTP {http_status}).'


def _render_verification_result(request, result, order=None, status_code=200):
    return render(
        request,
        'payment/verification.html',
        {
            'result': result,
            'order': order,
            'order_url': (
                reverse('order_confirmation', kwargs={'order_id': order.id})
                if order else None
            ),
        },
        status=status_code,
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_khalti_payment(request):
    order_id = request.data.get('order_id')
    try:
        order_id = int(order_id)
    except (TypeError, ValueError):
        return Response(
            {'error': 'A valid order_id is required.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.payment_status == 'paid':
        return Response(
            {'error': 'This order has already been paid.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    if order.status not in ('pending', 'confirmed'):
        return Response(
            {'error': 'Payment is not available for this order.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    secret_key = (settings.KHALTI_SECRET_KEY or '').strip()
    if not secret_key:
        return Response(
            {
                'error': (
                    'Khalti is not configured with a secret key.'
                ),
                'configuration_help': (
                    'Set KHALTI_SECRET_KEY to the secret key from your Khalti '
                    'merchant account, then restart Django.'
                ),
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )

    amount_paisa = int(order.total_amount * 100)
    if amount_paisa < 1000:
        return Response(
            {'error': 'Khalti payments must be at least Rs. 10.00.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    product_names = list(
        order.items.values_list('product_name', flat=True)
    )
    purchase_order_name = ', '.join(product_names) or f'Order #{order.id}'
    purchase_order_name = purchase_order_name[:100]
    try:
        shipping_phone = order.shipping_address.phone
    except Order.shipping_address.RelatedObjectDoesNotExist:
        shipping_phone = ''

    url = f"{settings.KHALTI_BASE_URL.rstrip('/')}/epayment/initiate/"
    headers = {"Authorization": f"key {secret_key}"}
    try:
        return_url = _get_khalti_return_url()
    except ValueError as error:
        logger.error('Invalid Khalti callback configuration: %s', error)
        return Response(
            {'error': str(error)},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )

    customer_info = {
        "name": order.user.get_full_name() or order.user.username,
        "email": order.user.email,
    }
    customer_phone = shipping_phone or order.user.phone_number
    if customer_phone:
        customer_info['phone'] = customer_phone

    payload = {
        "return_url": return_url,
        "website_url": settings.KHALTI_WEBSITE_URL,
        "amount": amount_paisa,
        "purchase_order_id": str(order.id),
        "purchase_order_name": purchase_order_name,
        "customer_info": customer_info,
    }

    with transaction.atomic():
        order = Order.objects.select_for_update().get(pk=order.pk)
        if order.payment_status == 'paid':
            return Response(
                {'error': 'This order has already been paid.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if order.status not in ('pending', 'confirmed'):
            return Response(
                {'error': 'Payment is not available for this order.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        now = timezone.now()
        KhaltiTransaction.objects.filter(
            order=order,
            status__in=('Initiated', 'Pending'),
            created_at__lt=now - ACTIVE_TRANSACTION_TIMEOUT,
        ).update(status='Expired')
        if KhaltiTransaction.objects.filter(
            order=order,
            status__in=('Initiated', 'Pending'),
            created_at__gte=now - ACTIVE_TRANSACTION_TIMEOUT,
        ).exists():
            return Response(
                {
                    'error': (
                        'A Khalti payment is already in progress for this order. '
                        'Complete or cancel it before trying again.'
                    )
                },
                status=status.HTTP_409_CONFLICT
            )

        payment_attempt = KhaltiTransaction.objects.create(
            order=order,
            amount_paisa=amount_paisa,
            status='Initiated',
        )

    try:
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=(10, 60),
        )
        try:
            data = response.json()
        except ValueError:
            _expire_payment_attempt(payment_attempt)
            logger.error(
                'Khalti initiation returned non-JSON response (HTTP %s).',
                response.status_code
            )
            return Response(
                {'error': 'Khalti returned an invalid response. Please try again.'},
                status=status.HTTP_502_BAD_GATEWAY
            )
    except requests.Timeout:
        _expire_payment_attempt(payment_attempt)
        logger.exception('Khalti payment initiation timed out.')
        return Response(
            {'error': 'Khalti did not respond in time. Please try again.'},
            status=status.HTTP_504_GATEWAY_TIMEOUT
        )
    except requests.ConnectionError:
        _expire_payment_attempt(payment_attempt)
        logger.exception('Khalti payment initiation request failed.')
        return Response(
            {
                'error': (
                    'The Django server could not reach Khalti. Check the '
                    'server internet connection, DNS, firewall, and proxy settings.'
                )
            },
            status=status.HTTP_502_BAD_GATEWAY
        )
    except requests.RequestException:
        _expire_payment_attempt(payment_attempt)
        logger.exception('Unexpected Khalti payment initiation request error.')
        return Response(
            {'error': 'Khalti payment request failed. Check the Django server logs.'},
            status=status.HTTP_502_BAD_GATEWAY
        )

    if (
        not response.ok
        or not isinstance(data, dict)
        or not data.get('pidx')
        or not data.get('payment_url')
    ):
        _expire_payment_attempt(payment_attempt)
        logger.warning(
            'Khalti payment initiation was rejected (HTTP %s, error key: %s).',
            response.status_code,
            data.get('error_key') if isinstance(data, dict) else None,
        )
        return Response(
            {
                'error': _gateway_error(data, response.status_code),
                'configuration_help': (
                    'For sandbox payments, confirm KHALTI_SECRET_KEY is the '
                    'secret key from your Khalti test merchant account, not a public key.'
                    if response.status_code in (401, 403)
                    else None
                ),
            },
            status=status.HTTP_502_BAD_GATEWAY
        )

    payment_attempt.pidx = data['pidx']
    payment_attempt.save(update_fields=['pidx'])
    return Response({
        'payment_url': data['payment_url'],
        'pidx': data['pidx']
    })


@api_view(['GET'])
@permission_classes([])
def verify_khalti_payment(request):
    pidx = request.query_params.get('pidx')
    if not pidx:
        return _render_verification_result(
            request,
            'error',
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    txn = KhaltiTransaction.objects.select_related('order').filter(
        pidx=pidx
    ).first()
    if not txn:
        return _render_verification_result(
            request,
            'error',
            status_code=status.HTTP_404_NOT_FOUND,
        )
    order = txn.order
    secret_key = (settings.KHALTI_SECRET_KEY or '').strip()
    if not secret_key:
        return _render_verification_result(request, 'error', order)

    url = f"{settings.KHALTI_BASE_URL.rstrip('/')}/epayment/lookup/"
    headers = {"Authorization": f"key {secret_key}"}
    try:
        response = requests.post(
            url,
            json={"pidx": pidx},
            headers=headers,
            timeout=15
        )
        data = response.json()
    except ValueError:
        logger.exception('Khalti returned invalid JSON during payment verification.')
        return _render_verification_result(request, 'error', order)
    except requests.Timeout:
        logger.exception('Khalti payment verification timed out.')
        return _render_verification_result(request, 'error', order)
    except requests.ConnectionError:
        logger.exception('Khalti payment verification connection failed.')
        return _render_verification_result(request, 'error', order)
    except requests.RequestException:
        logger.exception('Khalti payment verification request failed.')
        return _render_verification_result(request, 'error', order)

    if (
        not response.ok
        or not isinstance(data, dict)
        or data.get('pidx') != txn.pidx
    ):
        logger.warning(
            'Khalti payment verification was rejected (HTTP %s).',
            response.status_code
        )
        return _render_verification_result(request, 'error', order)

    status_map = {
        choice.casefold(): choice
        for choice, _label in KhaltiTransaction.STATUS_CHOICES
    }
    gateway_status = status_map.get(str(data.get('status', '')).casefold())
    if not gateway_status:
        logger.warning('Khalti returned an unknown payment status.')
        return _render_verification_result(request, 'pending', order)

    if gateway_status == 'Completed':
        try:
            verified_amount = int(data['total_amount'])
        except (KeyError, TypeError, ValueError):
            logger.warning('Khalti completion response did not include a valid amount.')
            return _render_verification_result(request, 'error', order)

        merchant_order_id = data.get('merchant_order_id')
        if merchant_order_id is None:
            merchant_order_id = data.get('purchase_order_id')
        if (
            verified_amount != txn.amount_paisa
            or (merchant_order_id is not None and str(merchant_order_id) != str(order.id))
        ):
            logger.error(
                'Khalti payment verification did not match order %s.',
                order.id
            )
            return _render_verification_result(request, 'error', order)

    with transaction.atomic():
        order = Order.objects.select_for_update().get(pk=order.pk)
        txn = KhaltiTransaction.objects.select_for_update().get(pk=txn.pk)
        txn.status = gateway_status
        txn.verified_at = timezone.now()
        txn.save(update_fields=['status', 'verified_at'])

        if gateway_status == 'Completed':
            order.payment_status = 'paid'
            update_fields = ['payment_status', 'updated_at']
            if order.status == 'pending':
                order.status = 'confirmed'
                update_fields.append('status')
            order.save(update_fields=update_fields)
            result = (
                'paid_cancelled'
                if order.status == 'cancelled'
                else 'success'
            )
        elif gateway_status in ('Expired', 'User canceled'):
            if order.payment_status != 'paid':
                order.payment_status = 'failed'
                order.save(update_fields=['payment_status', 'updated_at'])
            result = 'failed'
        else:
            result = 'pending'

    return _render_verification_result(request, result, order)
