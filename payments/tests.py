from decimal import Decimal
from unittest.mock import Mock, patch

import requests
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from orders.models import Order, OrderItem, ShippingAddress
from .models import KhaltiTransaction


@override_settings(
    KHALTI_SECRET_KEY='merchant-secret-from-portal',
    KHALTI_BASE_URL='https://payments.example.test/api/v2',
    KHALTI_RETURN_URL='https://shop.example.test/api/payments/verify/',
    KHALTI_WEBSITE_URL='https://shop.example.test/',
)
class KhaltiOrderIntegrationTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username='buyer',
            email='buyer@example.com',
            password='test-password',
            phone_number='9800000000',
        )
        self.order = Order.objects.create(
            user=self.user,
            total_amount=Decimal('125.50'),
        )
        OrderItem.objects.create(
            order=self.order,
            product_name='Notebook',
            quantity=2,
            price=Decimal('62.75'),
        )
        ShippingAddress.objects.create(
            order=self.order,
            full_name='Buyer',
            address='1 Paper Lane',
            city='Kathmandu',
            phone='9811111111',
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    @patch('payments.views.requests.post')
    def test_initiation_creates_order_transaction_and_returns_payment_url(self, post):
        post.return_value = Mock(
            ok=True,
            status_code=200,
            json=Mock(return_value={
                'pidx': 'payment-reference',
                'payment_url': 'https://khalti.example.test/pay',
            }),
        )

        response = self.client.post(
            reverse('khalti-initiate'),
            {'order_id': self.order.id},
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data['payment_url'],
            'https://khalti.example.test/pay',
        )
        post.assert_called_once()
        payload = post.call_args.kwargs['json']
        self.assertEqual(payload['amount'], 12550)
        self.assertEqual(
            payload['return_url'],
            'https://shop.example.test/payments/verify/',
        )
        self.assertEqual(payload['purchase_order_id'], str(self.order.id))
        self.assertEqual(payload['purchase_order_name'], 'Notebook')
        self.assertEqual(payload['customer_info']['phone'], '9811111111')
        self.assertEqual(
            post.call_args.kwargs['headers']['Authorization'],
            'key merchant-secret-from-portal',
        )
        self.assertEqual(post.call_args.kwargs['timeout'], (10, 60))
        self.assertTrue(
            KhaltiTransaction.objects.filter(
                order=self.order,
                pidx='payment-reference',
                amount_paisa=12550,
                status='Initiated',
            ).exists()
        )

    @patch('payments.views.requests.post')
    def test_gateway_rejection_exposes_actionable_error_without_creating_transaction(self, post):
        post.return_value = Mock(
            ok=False,
            status_code=401,
            json=Mock(return_value={
                'error_key': 'authentication_error',
                'detail': 'Invalid authorization key.',
            }),
        )

        response = self.client.post(
            reverse('khalti-initiate'),
            {'order_id': self.order.id},
            format='json',
        )

        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.data['error'], 'Invalid authorization key.')
        self.assertIn('secret key', response.data['configuration_help'])
        self.assertEqual(
            KhaltiTransaction.objects.get(order=self.order).status,
            'Expired',
        )

    @patch('payments.views.requests.post')
    def test_missing_khalti_secret_is_reported_before_gateway_call(self, post):
        with self.settings(KHALTI_SECRET_KEY=''):
            response = self.client.post(
                reverse('khalti-initiate'),
                {'order_id': self.order.id},
                format='json',
            )

        self.assertEqual(response.status_code, 503)
        self.assertIn('not configured', response.data['error'])
        self.assertIn('secret key', response.data['configuration_help'])
        post.assert_not_called()

    @patch('payments.views.requests.post', side_effect=requests.Timeout)
    def test_khalti_timeout_has_specific_error(self, post):
        response = self.client.post(
            reverse('khalti-initiate'),
            {'order_id': self.order.id},
            format='json',
        )

        self.assertEqual(response.status_code, 504)
        self.assertIn('did not respond in time', response.data['error'])

    @patch('payments.views.requests.post')
    def test_order_below_khalti_minimum_is_rejected_before_gateway_call(self, post):
        self.order.total_amount = Decimal('9.99')
        self.order.save(update_fields=['total_amount'])

        response = self.client.post(
            reverse('khalti-initiate'),
            {'order_id': self.order.id},
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('at least Rs. 10.00', response.data['error'])
        post.assert_not_called()

    def test_initiation_cannot_access_another_users_order(self):
        other_user = get_user_model().objects.create_user(
            username='other',
            email='other@example.com',
            password='test-password',
        )
        other_order = Order.objects.create(
            user=other_user,
            total_amount=Decimal('20.00'),
        )

        response = self.client.post(
            reverse('khalti-initiate'),
            {'order_id': other_order.id},
            format='json',
        )

        self.assertEqual(response.status_code, 404)

    @patch('payments.views.requests.post')
    def test_active_payment_reservation_prevents_second_initiation(self, post):
        post.return_value = Mock(
            ok=True,
            status_code=200,
            json=Mock(return_value={
                'pidx': 'active-payment-reference',
                'payment_url': 'https://khalti.example.test/pay',
            }),
        )

        first_response = self.client.post(
            reverse('khalti-initiate'),
            {'order_id': self.order.id},
            format='json',
        )
        second_response = self.client.post(
            reverse('khalti-initiate'),
            {'order_id': self.order.id},
            format='json',
        )

        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(second_response.status_code, 409)
        self.assertIn('already in progress', second_response.data['error'])
        self.assertEqual(post.call_count, 1)

    def test_active_payment_prevents_order_cancellation(self):
        KhaltiTransaction.objects.create(
            order=self.order,
            pidx='active-cancel-reference',
            amount_paisa=12550,
            status='Initiated',
        )
        client = Client()
        client.force_login(self.user)

        response = client.post(
            reverse('cancel_order', args=[self.order.id]),
        )

        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'pending')
        self.assertRedirects(
            response,
            f"{reverse('order_confirmation', args=[self.order.id])}"
            '?cancellation=payment_in_progress',
            fetch_redirect_response=False,
        )

    @patch('payments.views.requests.post')
    def test_cancelled_order_cannot_start_payment(self, post):
        self.order.status = 'cancelled'
        self.order.save(update_fields=['status'])

        response = self.client.post(
            reverse('khalti-initiate'),
            {'order_id': self.order.id},
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        post.assert_not_called()
        self.assertFalse(KhaltiTransaction.objects.filter(order=self.order).exists())

    def test_order_confirmation_connects_pay_button_and_csrf_cookie(self):
        client = Client()
        client.force_login(self.user)

        response = client.get(
            reverse('order_confirmation', args=[self.order.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('csrftoken', response.cookies)
        self.assertContains(response, reverse('khalti-initiate'))
        self.assertContains(response, 'Pay with Khalti')

    @patch('payments.views.requests.post')
    def test_verified_payment_marks_order_paid_and_returns_to_confirmation(self, post):
        txn = KhaltiTransaction.objects.create(
            order=self.order,
            pidx='completed-reference',
            amount_paisa=12550,
        )
        post.return_value = Mock(
            ok=True,
            status_code=200,
            json=Mock(return_value={
                'pidx': txn.pidx,
                'status': 'Completed',
                'total_amount': 12550,
                'merchant_order_id': str(self.order.id),
            }),
        )

        response = self.client.get(
            reverse('khalti-verify'),
            {'pidx': txn.pidx},
        )

        self.order.refresh_from_db()
        txn.refresh_from_db()
        self.assertEqual(self.order.payment_status, 'paid')
        self.assertEqual(self.order.status, 'confirmed')
        self.assertEqual(txn.status, 'Completed')
        self.assertIsNotNone(txn.verified_at)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payment/verification.html')
        self.assertContains(response, 'Payment Verified')
        self.assertContains(
            response,
            reverse('order_confirmation', args=[self.order.id]),
        )

        order_history_client = Client()
        order_history_client.force_login(self.user)
        history_response = order_history_client.get(reverse('order_history'))
        self.assertContains(history_response, 'Confirmed')
        self.assertContains(history_response, 'order-progress-step-active')

    @patch('payments.views.requests.post')
    def test_payment_with_wrong_amount_does_not_mark_order_paid(self, post):
        txn = KhaltiTransaction.objects.create(
            order=self.order,
            pidx='wrong-amount-reference',
            amount_paisa=12550,
        )
        post.return_value = Mock(
            ok=True,
            status_code=200,
            json=Mock(return_value={
                'pidx': txn.pidx,
                'status': 'Completed',
                'total_amount': 1,
                'merchant_order_id': str(self.order.id),
            }),
        )

        response = self.client.get(
            reverse('khalti-verify'),
            {'pidx': txn.pidx},
        )

        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, 'unpaid')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payment/verification.html')
        self.assertContains(response, 'Unable to Verify Payment')

    @patch('payments.views.requests.post')
    def test_late_completed_payment_does_not_reopen_cancelled_order(self, post):
        self.order.status = 'cancelled'
        self.order.save(update_fields=['status'])
        txn = KhaltiTransaction.objects.create(
            order=self.order,
            pidx='late-completed-reference',
            amount_paisa=12550,
        )
        post.return_value = Mock(
            ok=True,
            status_code=200,
            json=Mock(return_value={
                'pidx': txn.pidx,
                'status': 'Completed',
                'total_amount': 12550,
                'merchant_order_id': str(self.order.id),
            }),
        )

        response = self.client.get(
            reverse('khalti-verify'),
            {'pidx': txn.pidx},
        )

        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, 'paid')
        self.assertEqual(self.order.status, 'cancelled')
        self.assertContains(response, 'Payment Received for Cancelled Order')
