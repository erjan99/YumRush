from django.urls import path
from .views import *
urlpatterns = [

    path('registration/', UserRegisterView.as_view()),
    path('login/', UserLoginView.as_view()),
    path('profile/', UserProfileView.as_view()),
    path('user-otp-verification/', UserOTPVerificationView.as_view()),

]