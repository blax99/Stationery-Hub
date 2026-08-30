from django.shortcuts import render



def dashboard_view(request):

    context = {
        "total_products": 0,
        "total_orders": 0,
        "total_customers": 0,
        "total_revenue": 0,

        "pending_orders": 0,
        "processing_orders": 0,
        "completed_orders": 0,
        "cancelled_orders": 0,
    }

    return render(request, "admin_dashboard/dashboard.html", context)


def products_view(request):
    return render(request, "admin_dashboard/products.html")

def inventory_view(request):
    return render(request, "admin_dashboard/inventory.html")

def orders_view(request):
    return render(request, "admin_dashboard/orders.html")

def analytics_view(request):

    context = {
        # Summary cards
        "total_revenue": 125000,
        "total_orders": 150,
        "total_customers": 85,
        "total_products": 120,

        # Order status
        "pending_orders": 20,
        "processing_orders": 30,
        "completed_orders": 90,
        "cancelled_orders": 10,

        # Data for different date ranges
        "analytics_data": {
            "7": {
                "labels": [
                    "Aug 24",
                    "Aug 25",
                    "Aug 26",
                    "Aug 27",
                    "Aug 28",
                    "Aug 29",
                    "Aug 30"
                ],
                "revenue": [
                    3200,
                    4500,
                    3800,
                    5200,
                    4100,
                    6000,
                    5500
                ],
                "orders": [
                    4,
                    6,
                    5,
                    8,
                    7,
                    10,
                    9
                ]
            },

            "30": {
                "labels": [
                    "Week 1",
                    "Week 2",
                    "Week 3",
                    "Week 4"
                ],
                "revenue": [
                    28000,
                    32000,
                    30000,
                    35000
                ],
                "orders": [
                    32,
                    38,
                    35,
                    45
                ]
            },

            "6": {
                "labels": [
                    "March",
                    "April",
                    "May",
                    "June",
                    "July",
                    "August"
                ],
                "revenue": [
                    15000,
                    22000,
                    18000,
                    27000,
                    19000,
                    24000
                ],
                "orders": [
                    18,
                    25,
                    20,
                    32,
                    24,
                    31
                ]
            },

            "12": {
                "labels": [
                    "Sep",
                    "Oct",
                    "Nov",
                    "Dec",
                    "Jan",
                    "Feb",
                    "Mar",
                    "Apr",
                    "May",
                    "Jun",
                    "Jul",
                    "Aug"
                ],
                "revenue": [
                    12000,
                    14000,
                    16000,
                    19000,
                    21000,
                    17000,
                    15000,
                    22000,
                    18000,
                    27000,
                    19000,
                    24000
                ],
                "orders": [
                    15,
                    17,
                    21,
                    24,
                    28,
                    22,
                    18,
                    25,
                    20,
                    32,
                    24,
                    31
                ]
            },

            "year": {
                "labels": [
                    "Jan",
                    "Feb",
                    "Mar",
                    "Apr",
                    "May",
                    "Jun",
                    "Jul",
                    "Aug"
                ],
                "revenue": [
                    21000,
                    17000,
                    15000,
                    22000,
                    18000,
                    27000,
                    19000,
                    24000
                ],
                "orders": [
                    28,
                    22,
                    18,
                    25,
                    20,
                    32,
                    24,
                    31
                ]
            }
        }
    }

    return render(
        request,
        "admin_dashboard/analytics.html",
        context
    )