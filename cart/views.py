from django.shortcuts import render, redirect

from django.contrib.auth import get_user_model

User = get_user_model()

from products.models import Products

from .models import Cart, CartItem, Wishlist, WishlistItem

from django.http import JsonResponse

def cart(request):
    user = User.objects.get(username="testuser")
    cart, created = Cart.objects.get_or_create(user=user)
    cart_items = cart.items.all()

    print("CART ITEMS:")
    for item in cart_items:
        print(item.id, item.product.name, item.quantity)

    subtotal = sum(
        item.product.price * item.quantity
        for item in cart_items
    )

    return render(request, "cart/cart.html", {
        "cart": cart,
        "cart_items": cart_items,
        "subtotal": subtotal,
    })


def wishlist(request):
    return render(request, "cart/wishlist.html")


def add_to_cart(request, product_id):
    user = User.objects.get(username="testuser")
    product = Products.objects.get(id=product_id)

    cart, created = Cart.objects.get_or_create(user=user)

    quantity = int(request.POST.get("quantity", 1))

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity

    cart_item.save()

    return redirect("cart")


def update_cart_quantity(request, item_id):
    if request.method != "POST":
        return JsonResponse(
            {"success": False, "error": "Invalid request"},
            status=400
        )

    user = User.objects.get(username="testuser")
    cart = Cart.objects.get(user=user)

    cart_item = CartItem.objects.get(
        id=item_id,
        cart=cart
    )

    try:
        quantity = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        return JsonResponse(
            {"success": False, "error": "Invalid quantity"},
            status=400
        )

    stock = cart_item.product.stock

    if stock <= 0:
        cart_item.delete()
        return JsonResponse({
            "success": False,
            "error": "Product is out of stock"
        })

    if quantity < 1:
        quantity = 1

    if quantity > stock:
        quantity = stock

    cart_item.quantity = quantity
    cart_item.save()

    return JsonResponse({
        "success": True,
        "quantity": quantity
    })

def delete_cart_item(request, item_id):
    user = User.objects.get(username="testuser")
    cart = Cart.objects.get(user=user)

    cart_item = CartItem.objects.get(
        id=item_id,
        cart=cart
    )

    cart_item.delete()

    return redirect("cart")