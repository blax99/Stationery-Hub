from django.db import migrations


def confirm_paid_pending_orders(apps, schema_editor):
    Order = apps.get_model('orders', 'Order')
    Order.objects.filter(
        payment_status='paid',
        status='pending',
    ).update(status='confirmed')


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_repair_order_user_foreign_key'),
    ]

    operations = [
        migrations.RunPython(
            confirm_paid_pending_orders,
            migrations.RunPython.noop,
        ),
    ]
