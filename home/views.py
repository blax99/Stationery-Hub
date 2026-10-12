from django.shortcuts import render
from django.http import JsonResponse 
# Create your views here.


def home(request):
    return render(request, "home.html")
def chat_api(request):  # ← ADD THIS
    if request.method == 'POST':
        message = request.POST.get('message', '').lower()

        if 'hello' in message or 'hi' in message or 'hey' in message:
            reply = "Hi! Welcome to StationeryHub. How can I help you today?"
        elif 'price' in message or 'cost' in message or 'how much' in message:
            reply = "Our products range from Rs10 to Rs100. Check the product page for exact prices!"
        elif 'return' in message or 'refund' in message:
            reply = "We offer a 7-day return policy. Go to Profile → Orders → Request Return."
        elif 'delivery' in message or 'ship' in message or 'deliver' in message:
            reply = "We deliver within 3-5 business days. Free shipping on orders over Rs 25."
        elif 'track' in message or 'order status' in message or 'my order' in message:
            reply = "Go to Profile → Orders to track your shipment."
        elif 'pen' in message or 'pencil' in message or 'notebook' in message or 'stationery' in message:
            reply = "We have pens, pencils, notebooks, and more! Check our Products page."
        elif 'payment' in message or 'pay' in message or 'card' in message:
            reply = "We accept credit/debit cards and UPI. Payment is secure and encrypted."
        elif 'contact' in message or 'support' in message or 'help' in message:
            reply = "You can reach us at support@stationeryhub.com or use this chat."
        elif 'thank' in message or 'thanks' in message:
            reply = "You're welcome! Happy shopping at StationeryHub!"
        elif 'bye' in message:
            reply = "Goodbye! Come back anytime. Happy shopping! 👋"
        else:
            reply = "I can help with: prices, returns, delivery, order tracking, payments, or product info."

        return JsonResponse({"reply": reply})

    return JsonResponse({"error": "Method not allowed"}, status=405)