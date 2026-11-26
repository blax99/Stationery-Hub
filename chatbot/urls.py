from django.urls import path
from . import views

urlpatterns = [
    path("reply/", views.chat_reply, name="chat_reply"),
]