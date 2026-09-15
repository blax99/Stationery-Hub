from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Q
from .models import Category, Products  # Matches your model class name


def product_list(request, category_slug=None):
    selected_category = None
    
    # Annotate total product count for sidebar category list
    categories = Category.objects.annotate(
        total_products=Count('products', filter=Q(products__is_available=True))
    )
    
    # Prefetch relationships to avoid N+1 queries
    products = Products.objects.filter(is_available=True).select_related('category')

    # Filter by Category
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=selected_category)

    # Search Query Filter (?q=...)
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    # Sorting Filter (?sort=...)
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    else:
        products = products.order_by('-id')

    context = {
        'selected_category': selected_category,  # Matches template expectation
        'categories': categories,
        'products': products,
        'sort_by': sort_by,
    }
    return render(request, 'products/product_list.html', context)


def product_detail(request, slug):
    product = get_object_or_404(Products, slug=slug, is_available=True)
    
    related_products = Products.objects.filter(
        category=product.category, 
        is_available=True
    ).exclude(id=product.id)[:4]

    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'products/product_detail.html', context)