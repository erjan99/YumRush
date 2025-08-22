from django.urls import path
from .views import OrderRateAPIView

urlpatterns = [
    path('orders/<int:pk>/rate/', OrderRateAPIView.as_view(), name='rate_order'),
]