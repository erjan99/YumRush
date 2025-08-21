from drf_yasg.openapi import Response
from rest_framework import status
from rest_framework.views import APIView
from .models import *
from .serializer import *


class MainPageView(APIView):
    def get(self, request):
        categories = Category.objects.all()
        category_list_serializer = CategoryListSerializer(categories, many=True)

        category_id = request.query_params.get('category', None)
        if category_id:
            products = Product.objects.filter(category_id=category_id)
        else:
            products = Product.objects.all()

        products_list_serializer = ProductListSerializer(products, many=True)

        cart, created = Cart.objects.get_or_create(user=request.user, is_active=True)
        cart_serializer = CartSerializer(cart)

        data={
            'categories':category_list_serializer,
            'products':products_list_serializer,
            'cart':cart_serializer,
        }

        return Response(data)


