from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, PasswordResetRequestView, PasswordResetConfirmView, LoginPageView, ForgotPasswordPageView, RegisterPageView
from .views import RegisterView, PasswordResetRequestView, PasswordResetConfirmView, LoginPageView, ForgotPasswordPageView, RegisterPageView, ProfileView
from .views import RegisterView, PasswordResetRequestView, PasswordResetConfirmView, LoginPageView, ForgotPasswordPageView, RegisterPageView, ProfileView, ProfilePageView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('login/refresh/', TokenRefreshView.as_view(), name='login-refresh'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('login-page/', LoginPageView.as_view(), name='login-page'),
    path('forgot-password/', ForgotPasswordPageView.as_view(), name='forgot-password'),
    path('register-page/', RegisterPageView.as_view(), name='register-page'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile-page/', ProfilePageView.as_view(), name='profile-page'),
]