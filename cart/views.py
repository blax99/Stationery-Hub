from django.shortcuts import render

def cart(request):
    return render(request, "cart/cart.html")

# Create your views here.
def wishlist(request):
    return render(request, "cart/wishlist.html")