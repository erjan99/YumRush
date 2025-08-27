from django.urls import path
from .views import *

urlpatterns = [
    # Order management
    path('create/', CreateOrderView.as_view(), name='create_order'),
    path('history/', UserOrderHistoryView.as_view(), name='user_order_history'),
    path('order_history_detail/<ink:pk>/', OrderHistoryDetailView.as_view(), name='user_order_history_detail'),
    path('<int:pk>/rate/', OrderRateView.as_view(), name='rate_order'),

    # Courier orders
    path('courier/available_orders/', CourierOrdersView.as_view(), name='courier_orders'),
    path('courier/completed_orders/', CourierCompletedOrdersView.as_view(), name='courier_completed_orders'),

]