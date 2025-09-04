from django.urls import path
from .views import *


urlpatterns = [
    # Main page with products and cart
    path('main_page', MainPageView.as_view(), name='main_page'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
]