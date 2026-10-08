from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Products


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Products)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'category',
        'price',
        'stock',
        'is_available',
        'image_preview'
    )
    list_filter = ('category', 'is_available')
    list_editable = ('price', 'stock', 'is_available')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" '
                'style="object-fit:cover;border-radius:5px;" />',
                obj.image.url
            )
        return "No Image"

    image_preview.short_description = "Image"