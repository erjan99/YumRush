from django.urls import path
from .views import *

urlpatterns = [
    # Order management
    path('create/', CreateOrderView.as_view(), name='create_order'),
    path('history/', UserOrderHistoryView.as_view(), name='user_order_history'),
    path('<int:pk>/rate/', OrderRateView.as_view(), name='rate_order'),

    # Courier orders
    path('courier/orders/', CourierOrdersView.as_view(), name='courier_orders'),
]