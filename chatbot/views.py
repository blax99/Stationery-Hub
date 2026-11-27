import re
from decimal import Decimal

from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from cart.models import Cart
from orders.models import Order
from products.models import Products


PRODUCT_WORDS = {
    "product",
    "products",
    "pen",
    "pens",
    "pencil",
    "pencils",
    "notebook",
    "notebooks",
    "marker",
    "markers",
    "eraser",
    "erasers",
    "ruler",
    "rulers",
    "highlighter",
    "highlighters",
}
ORDER_WORDS = {"order", "orders", "track", "tracking"}
CART_WORDS = {"cart", "basket"}
PAYMENT_WORDS = {"payment", "payments", "pay", "paid"}
ORDER_QUERY_WORDS = {"order", "orders", "track", "tracking", "status"}
PRODUCT_QUERY_WORDS = {
    "available",
    "browse",
    "buy",
    "cost",
    "find",
    "have",
    "list",
    "looking",
    "much",
    "price",
    "recommend",
    "search",
    "show",
    "need",
    "want",
    "got",
}
PRODUCT_QUERY_STOP_WORDS = {
    "a",
    "about",
    "all",
    "an",
    "and",
    "are",
    "available",
    "browse",
    "buy",
    "can",
    "catalog",
    "catalogue",
    "cost",
    "do",
    "does",
    "everything",
    "find",
    "for",
    "got",
    "have",
    "how",
    "i",
    "in",
    "is",
    "item",
    "items",
    "list",
    "looking",
    "me",
    "m",
    "much",
    "need",
    "of",
    "please",
    "price",
    "product",
    "products",
    "recommend",
    "search",
    "see",
    "show",
    "some",
    "stock",
    "s",
    "tell",
    "the",
    "t",
    "what",
    "want",
    "where",
    "which",
    "you",
}


def _normalize_product_word(word):
    if len(word) > 4 and word.endswith("ies"):
        return f"{word[:-3]}y"
    if len(word) > 3 and word.endswith("s") and not word.endswith(
        ("is", "ss", "us")
    ):
        return word[:-1]
    return word


def _product_reply(message):
    words = re.findall(r"[a-z0-9]+", message.lower())
    query_words = [
        _normalize_product_word(word)
        for word in words
        if word not in PRODUCT_QUERY_STOP_WORDS
    ]
    products = Products.objects.filter(is_available=True, stock__gt=0).select_related(
        "category"
    )

    if query_words:
        matching_products = products
        for word in query_words:
            matching_products = matching_products.filter(
                Q(name__icontains=word)
                | Q(description__icontains=word)
                | Q(category__name__icontains=word)
                | Q(category__description__icontains=word)
            )
        results = list(matching_products.order_by("name"))
        if not results and len(query_words) > 1:
            search_terms = Q()
            for word in query_words:
                search_terms |= (
                    Q(name__icontains=word)
                    | Q(description__icontains=word)
                    | Q(category__name__icontains=word)
                    | Q(category__description__icontains=word)
                )
            results = list(products.filter(search_terms).order_by("name"))
        if not results:
            return (
                "I couldn't find an in-stock product matching that. "
                "Ask for a product name or browse the Products page."
            )
    else:
        results = list(products.order_by("name"))
        if not results:
            return "There are no in-stock products to show right now."

    details = []
    for index, product in enumerate(results, start=1):
        description = product.description.strip()
        if len(description) > 160:
            description = f"{description[:157].rstrip()}..."
        if not description:
            description = "No description available."
        elif description[-1] not in ".!?":
            description += "."
        details.append(
            f"[{index}] {product.name}\n"
            f"   Category: {product.category.name} | "
            f"Price: Rs. {product.price:.2f} | Stock: {product.stock} | "
            f"Description: {description}"
        )
    return "In-stock products:\n\n" + "\n\n".join(details)


def _order_reply(user, message):
    if user is None or not user.is_authenticated:
        return "Please sign in to view your orders and payment status."
    if user.role == "customer" and not user.is_email_verified:
        return "Please verify your email to view your orders and payment status."

    order_id_match = re.search(
        r"\border\s*(?:#|no\.?\s*)?\s*(\d+)\b", message, re.IGNORECASE
    )
    orders = Order.objects.filter(user=user).order_by("-created_at")
    if order_id_match:
        order = orders.filter(id=order_id_match.group(1)).first()
        if not order:
            return "I couldn't find that order in your account."
        matching_orders = [order]
    else:
        matching_orders = list(orders[:3])
        if not matching_orders:
            return "You don't have any orders yet."

    summaries = [
        (
            f"Order #{order.id:04d}: {order.get_status_display()}, "
            f"payment {order.get_payment_status_display().lower()}, "
            f"total Rs. {order.total_amount:.2f}."
        )
        for order in matching_orders
    ]
    return " ".join(summaries)


def _cart_reply(user):
    if not user.is_authenticated:
        return "Please sign in to view your cart."

    cart = (
        Cart.objects.filter(user=user)
        .prefetch_related("items__product")
        .first()
    )
    if not cart or not cart.items.exists():
        return "Your cart is empty."

    items = list(cart.items.all())
    total = sum(
        (item.product.price * item.quantity for item in items),
        start=Decimal("0.00"),
    )
    item_details = ", ".join(
        f"{item.product.name} x {item.quantity}" for item in items
    )
    return (
        f"Your cart has {len(items)} item types ({item_details}). "
        f"The subtotal is Rs. {total:.2f}."
    )


def get_reply(message, user=None):
    words = set(re.findall(r"[a-z]+", message.lower()))

    if words.intersection(PRODUCT_WORDS):
        return _product_reply(message)
    if words.intersection(ORDER_WORDS) or (
        words.intersection(PAYMENT_WORDS)
        and words.intersection(
            ORDER_QUERY_WORDS | {"paid", "unpaid", "failed", "transaction"}
        )
    ):
        return _order_reply(user, message)
    if words.intersection(CART_WORDS):
        return _cart_reply(user)
    if words.intersection(PAYMENT_WORDS):
        return (
            "Online payments are processed through Khalti. Place your order, "
            'then choose "Pay with Khalti" on the order confirmation page. '
            "The minimum Khalti payment is Rs. 10.00."
        )
    if "about" in words or words.intersection({"website", "site"}):
        return (
            "Stationery Hub is an online store for browsing and buying stationery, "
            "including pens, notebooks, pencils, and school and office supplies."
        )
    if words.intersection(PRODUCT_QUERY_WORDS):
        return _product_reply(message)
    if words.intersection({"hello", "hi", "hey"}):
        return (
            "Hello! I can tell you about Stationery Hub or help with products, "
            "orders, payment, or your cart. "
            'Try asking "Do you have a blue pen?"'
        )
    if words.intersection({"bye", "thanks", "thank"}):
        return "You're welcome! Thanks for visiting Stationery Hub."
    return "Ask me about the website, products, orders, payment, or your cart."


@require_POST
def chat_reply(request):
    message = request.POST.get("message", "").strip()
    if not message:
        return JsonResponse({"reply": "Please enter a question."}, status=400)
    if len(message) > 500:
        return JsonResponse(
            {"reply": "Please keep your question under 500 characters."},
            status=400,
        )
    return JsonResponse({"reply": get_reply(message, request.user)})
