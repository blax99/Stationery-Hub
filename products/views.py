from django.shortcuts import render, get_object_or_404
<<<<<<< HEAD
from django.db.models import Count, Q
=======
>>>>>>> d4b1eff9dab1543a61c27987199b640967670139
from .models import Category, Products


def product_list(request, category_slug=None):
<<<<<<< HEAD
    selected_category = None
    
    # Annotate total product count for sidebar category list
    categories = Category.objects.annotate(
        total_products=Count('products', filter=Q(products__is_available=True, products__stock__gt=0))
    )
    
    # Prefetch relationships to avoid N+1 queries
    products = Products.objects.filter(is_available=True, stock__gt=0).select_related('category')

    # Filter by Category
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=selected_category)

    # Search Query Filter (?q=...)
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    # Sorting Filter (?sort=...)
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    else:
        products = products.order_by('-created_at')

    context = {
        'selected_category': selected_category,
        'categories': categories,
        'products': products,
        'sort_by': sort_by,
    }
    return render(request, 'products/product_list.html', context)


def product_detail(request, slug):
    product = get_object_or_404(Products, slug=slug, is_available=True)
    
    related_products = Products.objects.filter(
        category=product.category, 
        is_available=True,
        stock__gt=0
=======
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
>>>>>>> d4b1eff9dab1543a61c27987199b640967670139
    ).exclude(id=product.id)[:4]

    context = {
        'product': product,
        'related_products': related_products,
    }
<<<<<<< HEAD
    return render(request, 'products/product_detail.html', context)
=======
    return render(request, 'products/detail.html', context)
>>>>>>> d4b1eff9dab1543a61c27987199b640967670139
