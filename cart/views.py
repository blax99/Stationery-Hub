from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
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

    for item in cart_items:
        item.item_total = item.product.price * item.quantity

    subtotal = sum(item.item_total for item in cart_items)

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

class CartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)

        cart_items = cart.items.all()

        items = []

        for item in cart_items:
            items.append({
                "id": item.id,
                "product": item.product.name,
                "price": item.product.price,
                "quantity": item.quantity,
                "item_total": item.product.price * item.quantity,
            })

        subtotal = sum(
            item.product.price * item.quantity
            for item in cart_items
        )

        return Response({
            "cart_id": cart.id,
            "items": items,
            "subtotal": subtotal,
        })

    def post(self, request):
        product_id = request.data.get("product_id")
        quantity = request.data.get("quantity", 1)

        if not product_id:
            return Response({
                "success": False,
                "error": "product_id is required"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            return Response({
                "success": False,
                "error": "quantity must be a number"
            }, status=status.HTTP_400_BAD_REQUEST)

        if quantity < 1:
            return Response({
                "success": False,
                "error": "quantity must be at least 1"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Products.objects.get(id=product_id)
        except Products.DoesNotExist:
            return Response({
                "success": False,
                "error": "Product not found"
            }, status=status.HTTP_404_NOT_FOUND)

        if quantity > product.stock:
            return Response({
                "success": False,
                "error": "Not enough stock"
            }, status=status.HTTP_400_BAD_REQUEST)

        cart, created = Cart.objects.get_or_create(
            user=request.user
        )

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product
        )

        if not created:
            new_quantity = cart_item.quantity + quantity

            if new_quantity > product.stock:
                return Response({
                    "success": False,
                    "error": "Not enough stock"
                }, status=status.HTTP_400_BAD_REQUEST)

            cart_item.quantity = new_quantity
        else:
            cart_item.quantity = quantity

        cart_item.save()

        return Response({
            "success": True,
            "message": "Product added to cart",
            "product": product.name,
            "quantity": cart_item.quantity
        }, status=status.HTTP_201_CREATED)

    def patch(self, request):
        item_id = request.data.get("item_id")
        quantity = request.data.get("quantity")

        if not item_id:
            return Response({
                "success": False,
                "error": "item_id is required"
            }, status=status.HTTP_400_BAD_REQUEST)

        if quantity is None:
            return Response({
                "success": False,
                "error": "quantity is required"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            return Response({
                "success": False,
                "error": "quantity must be a number"
            }, status=status.HTTP_400_BAD_REQUEST)

        if quantity < 1:
            return Response({
                "success": False,
                "error": "quantity must be at least 1"
            }, status=status.HTTP_400_BAD_REQUEST)

        cart = Cart.objects.get(user=request.user)

        try:
            cart_item = CartItem.objects.get(
                id=item_id,
                cart=cart
            )
        except CartItem.DoesNotExist:
            return Response({
                "success": False,
                "error": "Cart item not found"
            }, status=status.HTTP_404_NOT_FOUND)

        if quantity > cart_item.product.stock:
            return Response({
                "success": False,
                "error": "Not enough stock"
            }, status=status.HTTP_400_BAD_REQUEST)

        cart_item.quantity = quantity
        cart_item.save()

        return Response({
            "success": True,
            "message": "Cart quantity updated",
            "item_id": cart_item.id,
            "quantity": cart_item.quantity,
            "item_total": cart_item.product.price * cart_item.quantity
        })

    
    def delete(self, request):
        item_id = request.data.get("item_id")

        if not item_id:
            return Response({
                "success": False,
                "error": "item_id is required"
            }, status=status.HTTP_400_BAD_REQUEST)

        cart = Cart.objects.get(user=request.user)

        try:
            cart_item = CartItem.objects.get(
                id=item_id,
                cart=cart
            )
        except CartItem.DoesNotExist:
            return Response({
                "success": False,
                "error": "Cart item not found"
            }, status=status.HTTP_404_NOT_FOUND)

        cart_item.delete()

        return Response({
            "success": True,
            "message": "Product removed from cart"
        })