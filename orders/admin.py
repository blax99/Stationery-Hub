from django.contrib import admin
from .models import Order, ShippingAddress

admin.site.register(Order)
admin.site.register(ShippingAddress)

# Register your models here.
