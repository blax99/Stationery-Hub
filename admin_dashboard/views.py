from django.shortcuts import render, redirect
from django.db.models import Sum, Count
from django.db.models.functions import TruncDate, TruncMonth
from django.utils import timezone
from datetime import timedelta

from products.models import Products, Category
from products.forms import ProductForm
from orders.models import Order
from users.models import User


def dashboard_view(request):

    total_products = Products.objects.count()

    total_orders = Order.objects.count()

    total_customers = User.objects.filter(role="customer").count()

    total_revenue = Order.objects.aggregate(total=Sum("total_amount"))["total"] or 0

    pending_orders = Order.objects.filter(status="pending").count()

    processing_orders = Order.objects.filter(status="confirmed").count()

    completed_orders = Order.objects.filter(status="delivered").count()

    cancelled_orders = 0

    recent_orders = Order.objects.select_related("user").order_by("-created_at")[:5]

    today = timezone.localdate()

    seven_days_ago = today - timedelta(days=6)

    sales_data = (
        Order.objects.filter(
            created_at__date__gte=seven_days_ago, created_at__date__lte=today
        )
        .annotate(date=TruncDate("created_at"))
        .values("date")
        .annotate(revenue=Sum("total_amount"))
        .order_by("date")
    )

    sales_data_dict = {item["date"]: float(item["revenue"] or 0) for item in sales_data}

    sales_labels = []
    sales_revenue = []

    for i in range(7):
        current_date = seven_days_ago + timedelta(days=i)

        sales_labels.append(current_date.strftime("%b %d"))

        sales_revenue.append(sales_data_dict.get(current_date, 0))

    context = {
        "total_products": total_products,
        "total_orders": total_orders,
        "total_customers": total_customers,
        "total_revenue": total_revenue,
        "pending_orders": pending_orders,
        "processing_orders": processing_orders,
        "completed_orders": completed_orders,
        "cancelled_orders": cancelled_orders,
        "recent_orders": recent_orders,
        "sales_labels": sales_labels,
        "sales_revenue": sales_revenue,
    }

    return render(request, "admin_dashboard/dashboard.html", context)


def products_view(request):

    form = ProductForm()

    if request.method == "POST":

        product_id = request.POST.get("product_id")
        delete_id = request.POST.get("delete_id")

        # Delete Product
        if delete_id:
            Products.objects.filter(id=delete_id).delete()

        # Edit Product
        elif product_id:
            product = Products.objects.get(id=product_id)

            form = ProductForm(request.POST, request.FILES, instance=product)

            if form.is_valid():
                form.save()

        # Add Product
        else:
            form = ProductForm(request.POST, request.FILES)

            if form.is_valid():
                form.save()

    products = Products.objects.select_related("category").all()
    categories = Category.objects.all()

    context = {
        "products": products,
        "categories": categories,
        "form": form,
    }

    return render(request, "admin_dashboard/products.html", context)


def inventory_view(request):

    if request.method == "POST":

        product_id = request.POST.get("product_id")
        stock = request.POST.get("stock")

        if product_id and stock is not None:

            try:
                stock = int(stock)

                if stock >= 0:
                    product = Products.objects.filter(id=product_id).first()

                    if product:
                        product.stock = stock
                        product.save()

            except (ValueError, TypeError):
                pass

    products = Products.objects.select_related("category").all()

    context = {"products": products}

    return render(request, "admin_dashboard/inventory.html", context)


def orders_view(request):

    if request.method == "POST":

        order_id = request.POST.get("order_id")
        action = request.POST.get("action")

        if order_id and action:

            order = Order.objects.filter(id=order_id).first()

            if order:

                if action == "approve" and order.status == "pending":
                    order.status = "confirmed"
                    order.save()

                elif action == "ship" and order.status == "confirmed":
                    order.status = "shipped"
                    order.save()

                elif action == "deliver" and order.status == "shipped":
                    order.status = "delivered"
                    order.save()

    orders = (
        Order.objects.select_related("user", "shipping_address")
        .prefetch_related("items")
        .all()
    )

    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status="pending").count()
    confirmed_orders = Order.objects.filter(status="confirmed").count()
    shipped_orders = Order.objects.filter(status="shipped").count()
    delivered_orders = Order.objects.filter(status="delivered").count()

    context = {
        "orders": orders,
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "confirmed_orders": confirmed_orders,
        "shipped_orders": shipped_orders,
        "delivered_orders": delivered_orders,
    }

    return render(request, "admin_dashboard/orders.html", context)


def analytics_view(request):

    total_products = Products.objects.count()

    total_orders = Order.objects.count()

    total_customers = User.objects.filter(role="customer").count()

    total_revenue = Order.objects.aggregate(total=Sum("total_amount"))["total"] or 0

    pending_orders = Order.objects.filter(status="pending").count()

    processing_orders = Order.objects.filter(status="confirmed").count()

    completed_orders = Order.objects.filter(status="delivered").count()

    # No cancelled status in the current model
    cancelled_orders = 0

    today = timezone.localdate()

    def get_status_data(queryset):
        return {
            "pending": queryset.filter(status="pending").count(),
            "confirmed": queryset.filter(status="confirmed").count(),
            "shipped": queryset.filter(status="shipped").count(),
            "delivered": queryset.filter(status="delivered").count(),
        }

    seven_days_ago = today - timedelta(days=6)

    orders_7_days = Order.objects.filter(
        created_at__date__gte=seven_days_ago, created_at__date__lte=today
    )

    daily_data = (
        orders_7_days.annotate(date=TruncDate("created_at"))
        .values("date")
        .annotate(revenue=Sum("total_amount"), orders=Count("id"))
        .order_by("date")
    )

    labels_7 = []
    revenue_7 = []
    orders_7 = []

    daily_data_dict = {item["date"]: item for item in daily_data}

    for i in range(7):

        current_date = seven_days_ago + timedelta(days=i)

        labels_7.append(current_date.strftime("%b %d"))

        item = daily_data_dict.get(current_date)

        if item:

            revenue_7.append(float(item["revenue"] or 0))

            orders_7.append(item["orders"])

        else:

            revenue_7.append(0)
            orders_7.append(0)

    thirty_days_ago = today - timedelta(days=29)

    orders_30_days = Order.objects.filter(
        created_at__date__gte=thirty_days_ago, created_at__date__lte=today
    )

    daily_data_30 = (
        orders_30_days.annotate(date=TruncDate("created_at"))
        .values("date")
        .annotate(revenue=Sum("total_amount"), orders=Count("id"))
        .order_by("date")
    )

    labels_30 = []
    revenue_30 = []
    orders_30 = []

    daily_data_30_dict = {item["date"]: item for item in daily_data_30}

    for i in range(30):

        current_date = thirty_days_ago + timedelta(days=i)

        labels_30.append(current_date.strftime("%b %d"))

        item = daily_data_30_dict.get(current_date)

        if item:

            revenue_30.append(float(item["revenue"] or 0))

            orders_30.append(item["orders"])

        else:

            revenue_30.append(0)
            orders_30.append(0)

    six_months_ago = today.replace(day=1) - timedelta(days=150)

    orders_6_months = Order.objects.filter(
        created_at__date__gte=six_months_ago, created_at__date__lte=today
    )

    monthly_data_6 = (
        orders_6_months.annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(revenue=Sum("total_amount"), orders=Count("id"))
        .order_by("month")
    )

    labels_6 = []
    revenue_6 = []
    orders_6 = []

    monthly_data_6_dict = {
        item["month"].date().replace(day=1): item for item in monthly_data_6
    }

    current_month = today.replace(day=1)

    months_6 = []

    year = current_month.year
    month = current_month.month

    for _ in range(6):

        months_6.append(current_month.replace(year=year, month=month, day=1))

        month -= 1

        if month == 0:
            month = 12
            year -= 1

    months_6.reverse()

    for current_date in months_6:

        labels_6.append(current_date.strftime("%b %Y"))

        item = monthly_data_6_dict.get(current_date)

        if item:

            revenue_6.append(float(item["revenue"] or 0))

            orders_6.append(item["orders"])

        else:

            revenue_6.append(0)
            orders_6.append(0)

    twelve_months_ago = today.replace(day=1) - timedelta(days=335)

    orders_12_months = Order.objects.filter(
        created_at__date__gte=twelve_months_ago, created_at__date__lte=today
    )

    monthly_data_12 = (
        orders_12_months.annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(revenue=Sum("total_amount"), orders=Count("id"))
        .order_by("month")
    )

    labels_12 = []
    revenue_12 = []
    orders_12 = []

    monthly_data_12_dict = {
        item["month"].date().replace(day=1): item for item in monthly_data_12
    }

    current_month = today.replace(day=1)

    months_12 = []

    year = current_month.year
    month = current_month.month

    for _ in range(12):

        months_12.append(current_month.replace(year=year, month=month, day=1))

        month -= 1

        if month == 0:
            month = 12
            year -= 1

    months_12.reverse()

    for current_date in months_12:

        labels_12.append(current_date.strftime("%b %Y"))

        item = monthly_data_12_dict.get(current_date)

        if item:

            revenue_12.append(float(item["revenue"] or 0))

            orders_12.append(item["orders"])

        else:

            revenue_12.append(0)
            orders_12.append(0)

    start_of_year = today.replace(month=1, day=1)

    orders_this_year = Order.objects.filter(
        created_at__date__gte=start_of_year, created_at__date__lte=today
    )

    monthly_data_year = (
        orders_this_year.annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(revenue=Sum("total_amount"), orders=Count("id"))
        .order_by("month")
    )

    labels_year = []
    revenue_year = []
    orders_year = []

    monthly_data_year_dict = {
        item["month"].date().replace(day=1): item for item in monthly_data_year
    }

    current_month = start_of_year

    while current_month <= today.replace(day=1):

        labels_year.append(current_month.strftime("%b %Y"))

        item = monthly_data_year_dict.get(current_month)

        if item:

            revenue_year.append(float(item["revenue"] or 0))

            orders_year.append(item["orders"])

        else:

            revenue_year.append(0)
            orders_year.append(0)

        if current_month.month == 12:

            current_month = current_month.replace(year=current_month.year + 1, month=1)

        else:

            current_month = current_month.replace(month=current_month.month + 1)

    analytics_data = {
        "7": {
            "labels": labels_7,
            "revenue": revenue_7,
            "orders": orders_7,
        },
        "30": {
            "labels": labels_30,
            "revenue": revenue_30,
            "orders": orders_30,
        },
        "6": {
            "labels": labels_6,
            "revenue": revenue_6,
            "orders": orders_6,
        },
        "12": {
            "labels": labels_12,
            "revenue": revenue_12,
            "orders": orders_12,
        },
        "year": {
            "labels": labels_year,
            "revenue": revenue_year,
            "orders": orders_year,
        },
    }

    context = {
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "total_customers": total_customers,
        "total_products": total_products,
        "pending_orders": pending_orders,
        "processing_orders": processing_orders,
        "completed_orders": completed_orders,
        "cancelled_orders": cancelled_orders,
        "analytics_data": analytics_data,
    }

    return render(request, "admin_dashboard/analytics.html", context)


def users_view(request):

    if request.method == "POST":
        action = request.POST.get("action")

        # Add user
        if action == "add":
            full_name = request.POST.get("full_name", "").strip()
            email = request.POST.get("email", "").strip()
            password = request.POST.get("password")
            role = request.POST.get("role")

            name_parts = full_name.split()
            first_name = name_parts[0] if name_parts else ""
            last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

            username = email.split("@")[0]
            original_username = username
            counter = 1

            while User.objects.filter(username=username).exists():
                username = f"{original_username}{counter}"
                counter += 1

            User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role=role,
                is_active=True,
            )

            return redirect("users")

        # Edit user
        elif action == "edit":
            user_id = request.POST.get("user_id")
            user = User.objects.get(id=user_id)

            full_name = request.POST.get("full_name", "").strip()
            email = request.POST.get("email", "").strip()
            password = request.POST.get("password")
            role = request.POST.get("role")

            name_parts = full_name.split()

            user.first_name = name_parts[0] if name_parts else ""
            user.last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
            user.email = email
            user.role = role

            if password:
                user.set_password(password)

            user.save()

            return redirect("users")

        # Delete user
        elif action == "delete":
            user_id = request.POST.get("user_id")
            user = User.objects.get(id=user_id)
            user.delete()

            return redirect("users")

    users = User.objects.all().order_by("-date_joined")

    total_users = users.count()
    total_customers = users.filter(role="customer").count()
    total_admins = users.filter(role="admin").count()

    context = {
        "users": users,
        "total_users": total_users,
        "total_customers": total_customers,
        "total_admins": total_admins,
    }

    return render(request, "admin_dashboard/users.html", context)
