from django.db import migrations
from django.utils.text import slugify


def create_initial_categories(apps, schema_editor):
    Category = apps.get_model('products', 'Category')
    categories = [
        "Notebooks & Paper",
        "Pens & Writing",
        "Desk & Essentials",
        "Sets & Gifts",
    ]
    for cat_name in categories:
        Category.objects.get_or_create(
            name=cat_name,
            defaults={'slug': slugify(cat_name)},
        )


def reverse_initial_categories(apps, schema_editor):
    Category = apps.get_model('products', 'Category')
    Category.objects.filter(name__in=[
        "Notebooks & Paper",
        "Pens & Writing",
        "Desk & Essentials",
        "Sets & Gifts",
    ]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_initial_categories, reverse_code=reverse_initial_categories),
    ]