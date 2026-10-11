from django.db import migrations
from django.utils.text import slugify


OLD_CATEGORY_NAMES = {"pencils and lead"}


def normalize_name(value):
    return " ".join(value.strip().lower().replace("&", "and").split())


def unique_slug(categories, name, exclude_pk=None):
    base_slug = slugify(name)
    slug = base_slug
    counter = 1
    while categories.filter(slug=slug).exclude(pk=exclude_pk).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug


def update_categories(apps, schema_editor):
    Category = apps.get_model("products", "Category")
    Product = apps.get_model("products", "Products")
    database = schema_editor.connection.alias
    categories = Category.objects.using(database)
    products = Product.objects.using(database)

    pencils_categories = [
        category
        for category in categories.all()
        if normalize_name(category.name) in OLD_CATEGORY_NAMES
    ]

    pens_category = categories.filter(name__iexact="Pens").first()
    if pens_category is None:
        pens_category = categories.filter(name__iexact="Pens & Writing").first()
        if pens_category:
            pens_category.name = "Pens"
            pens_category.slug = unique_slug(categories, "Pens", pens_category.pk)
            pens_category.save(using=database, update_fields=["name", "slug"])
        else:
            pens_category = categories.create(
                name="Pens", slug=unique_slug(categories, "Pens")
            )

    for category in pencils_categories:
        products.filter(category_id=category.pk).update(category_id=pens_category.pk)
        category.delete(using=database)

    if not categories.filter(name__iexact="Sports").exists():
        categories.create(name="Sports", slug=unique_slug(categories, "Sports"))


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0003_alter_category_options_products_delete_product_and_more"),
    ]

    operations = [
        migrations.RunPython(update_categories, reverse_code=migrations.RunPython.noop),
    ]
