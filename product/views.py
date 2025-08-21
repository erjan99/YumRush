from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from order.models import CartItem, Cart
from order.serializers import CartSerializer
from .serializers import *


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

        data = {
            'categories': category_list_serializer,
            'products': products_list_serializer,
            'cart': cart_serializer,
        }

        return Response(data)

    def post(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        if not product_id:
            return Response({'Error:': 'Product ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        product = Product.objects.get(id=product_id)
        cart_item, created = CartItem.objects.get_or_create(product=product, cart=cart)

        new_quantity = cart_item.quantity + quantity

        if new_quantity < 0:
            cart_item.delete()
        else:
            cart_item.quantity = new_quantity
            cart_item.save()

        cart_serializer = CartSerializer(cart)
        return Response(cart_serializer.data)


class ProductDetailView(APIView):

    def get(self, request, pk):
        product = Product.objects.get(pk=pk)
        serializer = ProductDetailSerializer(product)
        return Response(serializer.data)
