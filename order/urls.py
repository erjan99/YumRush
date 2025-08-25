from django.urls import path
from .views import OrderRateAPIView, UserOrderHistoryView

urlpatterns = [
    # Оценка заказа
    path('<int:pk>/rate/', OrderRateAPIView.as_view(), name='rate_order'),
    # История заказа пользователя
    path('history/', UserOrderHistoryView.as_view(), name='order_history'),
]