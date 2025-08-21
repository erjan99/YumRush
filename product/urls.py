from django.urls import path
from .views import *

urlpatterns = [
    path('main-page/', MainPageView.as_view(), name='main_page'),
    path('product-detail/<int:pk>/', ProductDetailView.as_view(), name='detail_product'),
]