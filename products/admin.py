# #from django.contrib import admin

# # Register your models here.
# from django.contrib import admin
# from .models import Category, Products

# @admin.register(Category)
# class CategoryAdmin(admin.ModelAdmin):
#     list_display = ('name', 'slug')
#     prepopulated_fields = {'slug': ('name',)}

# @admin.register(Products)
# class ProductAdmin(admin.ModelAdmin):
#     list_display = ('name', 'category', 'price', 'stock', 'is_available')
#     list_filter = ('category', 'is_available')
#     list_editable = ('price', 'stock', 'is_available')
#     search_fields = ('name',)
#     prepopulated_fields = {'slug': ('name',)} 


from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Products


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Products)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('thumbnail', 'name', 'category', 'price', 'stock', 'is_available')
    list_filter = ('category', 'is_available')
    list_editable = ('price', 'stock', 'is_available')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

    def thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:40px;border-radius:4px;" />', obj.image.url)
        return "—"
    thumbnail.short_description = 'Image'