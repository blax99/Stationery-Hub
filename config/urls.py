from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', include('admin_dashboard.urls')),
    path('', include('home.urls')),
    path('products/', include('products.urls')),
    path('users/', include('users.urls')),
    path('api/users/', include('users.urls')),
    path('api/products/', include('products.api_urls')),
    path('cart/', include('cart.urls')),
    path('api/cart/', include('cart.api_urls')),
    path('orders/', include('orders.urls')), 
    path('api/orders/', include('orders.api_urls')),
    path('api/payments/', include('payments.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)   