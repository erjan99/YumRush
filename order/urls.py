from django.urls import path
from .views import OrderRateAPIView, CreateOrderView

urlpatterns = [
    path('orders/<int:pk>/rate/', OrderRateAPIView.as_view(), name='rate_order'),

    path('create_order/', CreateOrderView.as_view())
]