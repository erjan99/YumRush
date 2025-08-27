from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from order.models import CartItem, Cart
from order.serializers import CartSerializer
from .serializers import *


class MainPageView(APIView):
    @swagger_auto_schema(
        tags=['main_page'],
        operation_description="Get main page data with categories, products and cart",
        manual_parameters=[
            openapi.Parameter('category', openapi.IN_QUERY,
                              description="Filter products by category ID", type=openapi.TYPE_INTEGER)
        ],
        responses={
            200: openapi.Response(
                description="Main page data",
                examples={
                    "application/json": {
                        "categories": [
                            {"id": 1, "name": "Burgers", "image": "http://example.com/media/categories/burgers.jpg"}
                        ],
                        "products": [
                            {"id": 1, "name": "Cheeseburger", "image": "http://example.com/media/products/cheeseburger.jpg",
                             "original_price": 10.99, "discounted_price": 8.99,
                             "category": {"id": 1, "name": "Burgers", "image": "http://example.com/media/categories/burgers.jpg"},
                             "rating": 4.5,
                             "company": {"id": 1, "name": "Company Name", "logo": "http://example.com/media/companies/logo.png"},
                             "grams": 250}
                        ],
                        "cart": {
                            "id": 1,
                            "items": [
                                {"id": 1, "product": {"id": 1, "name": "Cheeseburger"}, "quantity": 2, "total_price": 17.98}
                            ],
                            "total_price": 17.98
                        }
                    }
                }
            )
        }
    )
    def get(self, request):
        categories = Category.objects.all()
        category_list_serializer = CategoryListSerializer(categories, many=True, context={'request': request})

        category_id = request.query_params.get('category', None)
        if category_id:
            try:
                products = Product.objects.filter(category_id=int(category_id))
            except ValueError:
                return Response({
                    'error': 'Неверный ID категории'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            products = Product.objects.all()

        products_list_serializer = ProductListSerializer(products, many=True, context={'request': request})

        cart = None
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user, is_active=True)

        cart_serializer = CartSerializer(cart) if cart else None

        data = {
            'categories': category_list_serializer.data,
            'products': products_list_serializer.data,
            'cart': cart_serializer.data if cart_serializer else None,
        }

        return Response(data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=['main_page'],
        operation_description="Add product to cart",
        request_body=AddToCartSerializer,
        responses={
            200: CartSerializer,
            400: "Bad request - invalid data",
            401: "Authentication required",
            404: "Product not found"
        }
    )
    def post(self, request):
        if not request.user.is_authenticated:
            return Response({
                'error': 'Требуется аутентификация'
            }, status=status.HTTP_401_UNAUTHORIZED)

        cart, created = Cart.objects.get_or_create(
            user=request.user,
            is_active=True
        )

        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        if not product_id:
            return Response({
                'error': 'ID продукта обязателен'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            quantity = int(quantity)
            if quantity < -100 or quantity > 100:  # Разумные ограничения
                return Response({
                    'error': 'Количество должно быть от -100 до 100'
                }, status=status.HTTP_400_BAD_REQUEST)
        except (ValueError, TypeError):
            return Response({
                'error': 'Неверное количество'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({
                'error': 'Продукт не найден'
            }, status=status.HTTP_404_NOT_FOUND)

        cart_item, created = CartItem.objects.get_or_create(
            product=product,
            cart=cart,
            defaults={'quantity': 0}
        )

        new_quantity = cart_item.quantity + quantity

        if new_quantity <= 0:
            cart_item.delete()
        else:
            cart_item.quantity = new_quantity
            cart_item.save()

        cart_serializer = CartSerializer(cart)
        return Response(cart_serializer.data, status=status.HTTP_200_OK)


class ProductDetailView(APIView):
    @swagger_auto_schema(
        tags=['product'],
        operation_description="Get detailed information about a product",
        responses={
            200: ProductDetailSerializer,
            404: "Product not found",
            400: "Invalid product ID"
        }
    )
    def get(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({
                'error': 'Продукт не найден'
            }, status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response({
                'error': 'Неверный ID продукта'
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = ProductDetailSerializer(product, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)