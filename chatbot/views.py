import re

from django.http import JsonResponse
from django.views.decorators.http import require_POST

REPLIES = [
    (("hello", "hi", "hey"), "Hello! Welcome to Stationery Hub. How can I help?"),
    (("product", "products", "pen", "notebook"), "Please visit our Products page to see what's available."),
    (("order", "track"), "Please check your order page for order details."),
    (("payment", "pay"), "You can see the payment options at checkout."),
    (("cart",), "Open your cart to view or change your items."),
    (("bye", "thanks"), "Thank you for visiting Stationery Hub!"),
]


def get_reply(message):
    words = set(re.findall(r"[a-z]+", message.lower()))
    # Check specific topics before greetings
    for keywords, reply in REPLIES[1:] + REPLIES[:1]:
        if words.intersection(keywords):
            return reply
    return "Sorry, I don't understand. Ask about products, orders, payment or cart."


@require_POST
def chat_reply(request):
    message = request.POST.get("message", "")
    return JsonResponse({"reply": get_reply(message)})