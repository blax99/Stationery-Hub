from django.db import models
from orders.models import Order


class KhaltiTransaction(models.Model):
    STATUS_CHOICES = [
        ('Initiated', 'Initiated'),
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Expired', 'Expired'),
        ('User canceled', 'User canceled'),
        ('Refunded', 'Refunded'),
    ]

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='khalti_transactions'
    )
    pidx = models.CharField(max_length=100, unique=True, blank=True, null=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Initiated')
    amount_paisa = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.pidx} - {self.status}"