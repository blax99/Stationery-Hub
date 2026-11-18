from django.shortcuts import redirect
from django.contrib import messages


def email_verification_required(view_func):
    """
    Decorator that blocks unverified customers from accessing order/payment views.
    Admins and superusers bypass this check.
    """

    def wrapper(request, *args, **kwargs):
        if (
            request.user.is_authenticated
            and request.user.role == "customer"
            and not request.user.is_email_verified
        ):
            messages.error(
                request,
                "Please verify your email address before placing orders or making payments.",
            )
            return redirect("verify-email")
        return view_func(request, *args, **kwargs)

    return wrapper