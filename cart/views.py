from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from products.models import Products
from .models import Cart, CartItem, Wishlist, WishlistItem


def cart(request):
    user = User.objects.get(username="testuser")
    cart = Cart.objects.get(user=user)
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
    

    user = User.objects.get(username="testuser")
    cart = Cart.objects.get(user=user)

    cart_item = CartItem.objects.get(
        id=item_id,
        cart=cart
    )

    

    quantity = int(request.POST.get("quantity", 1))

    if quantity < 1:
        quantity = 1

    if quantity > cart_item.product.stock:
        quantity = cart_item.product.stock

    cart_item.quantity = quantity
    cart_item.save()

   

    return redirect("cart")

def delete_cart_item(request, item_id):
    user = User.objects.get(username="testuser")
    cart = Cart.objects.get(user=user)

    cart_item = CartItem.objects.get(
        id=item_id,
        cart=cart
    )

    cart_item.delete()

    return redirect("cart")