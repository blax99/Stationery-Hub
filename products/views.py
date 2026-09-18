from django.shortcuts import render, get_object_or_404
from .models import Category, Products


def product_list(request, category_slug=None):
    category = None
    # Pre-fetch active categories ordered by name
    categories = Category.objects.all()
    # Filter available products and join category data using select_related to avoid N+1 queries
    products = Products.objects.filter(is_available=True).select_related('category')

    # If a category slug is passed in the URL, filter products by that category
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    context = {
        'category': category,
        'categories': categories,
        'products': products,
    }
    return render(request, 'products/list.html', context)


def product_detail(request, slug):
    # Fetch product by slug ensuring it's available
    product = get_object_or_404(Products, slug=slug, is_available=True)
    
    # Fetch related products from the same category (excluding the current product)
    related_products = Products.objects.filter(
        category=product.category, 
        is_available=True
    ).exclude(id=product.id)[:4]

    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'products/detail.html', context)