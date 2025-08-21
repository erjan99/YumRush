from django.urls import path
from .views import *

urlpatterns = [
    path('main-page/', MainPageView.as_view(), name='main_page'),
]