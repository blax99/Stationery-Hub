from django.db import migrations


def repair_order_user_foreign_key(apps, schema_editor):
    order_model = apps.get_model('orders', 'Order')
    order_table = order_model._meta.db_table
    user_table = order_model._meta.get_field('user').remote_field.model._meta.db_table
    connection = schema_editor.connection
    quote_name = connection.ops.quote_name

    with connection.cursor() as cursor:
        constraints = connection.introspection.get_constraints(cursor, order_table)
        user_foreign_keys = {
            name: details
            for name, details in constraints.items()
            if details.get('foreign_key') and details.get('columns') == ['user_id']
        }

        if user_foreign_keys and all(
            details['foreign_key'] == (user_table, 'id')
            for details in user_foreign_keys.values()
        ):
            return

        has_correct_foreign_key = any(
            details['foreign_key'] == (user_table, 'id')
            for details in user_foreign_keys.values()
        )

        cursor.execute(
            f'SELECT COUNT(*) FROM {quote_name(order_table)} AS order_row '
            f'LEFT JOIN {quote_name(user_table)} AS user_row '
            f'ON order_row.{quote_name("user_id")} = user_row.{quote_name("id")} '
            f'WHERE order_row.{quote_name("user_id")} IS NOT NULL '
            f'AND user_row.{quote_name("id")} IS NULL'
        )
        orphaned_orders = cursor.fetchone()[0]

    if orphaned_orders:
        raise RuntimeError(
            'Cannot update orders_order.user_id foreign key: '
            f'{orphaned_orders} orders have no matching custom user.'
        )

    for name, details in user_foreign_keys.items():
        if details['foreign_key'] != (user_table, 'id'):
            schema_editor.execute(
                f'ALTER TABLE {quote_name(order_table)} '
                f'DROP CONSTRAINT {quote_name(name)}'
            )

    if not has_correct_foreign_key:
        schema_editor.execute(
            f'ALTER TABLE {quote_name(order_table)} '
            f'ADD CONSTRAINT {quote_name("orders_order_user_id_users_user_id_fk")} '
            f'FOREIGN KEY ({quote_name("user_id")}) '
            f'REFERENCES {quote_name(user_table)} ({quote_name("id")}) '
            'DEFERRABLE INITIALLY DEFERRED'
        )


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_alter_order_status'),
        ('users', '0003_user_is_email_verified'),
    ]

    operations = [
        migrations.RunPython(repair_order_user_foreign_key),
    ]
