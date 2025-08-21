from rest_framework.response import Response
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

        # Don't try to get cart for anonymous users
        cart_data = None
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user, is_active=True)
            cart_serializer = CartSerializer(cart)
            cart_data = cart_serializer.data

        data = {
            'categories': category_list_serializer.data,  # Use .data here
            'products': products_list_serializer.data,    # Use .data here
            'cart': cart_data,
        }

        return Response(data)

    def post(self, request):
        # Add authentication check for post
        if not request.user.is_authenticated:
            return Response({'Error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

        cart, created = Cart.objects.get_or_create(user=request.user, is_active=True)
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        if not product_id:
            return Response({'Error': 'Product ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'Error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        cart_item, created = CartItem.objects.get_or_create(product=product, cart=cart)
        new_quantity = cart_item.quantity + quantity

        if new_quantity <= 0:
            cart_item.delete()
        else:
            cart_item.quantity = new_quantity
            cart_item.save()

        cart_serializer = CartSerializer(cart)
        return Response(cart_serializer.data)


