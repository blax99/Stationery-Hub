from django.urls import path
from . import views

urlpatterns = [
    path('initiate/', views.initiate_khalti_payment, name='khalti-initiate'),
    path('verify/', views.verify_khalti_payment, name='khalti-verify'),
]