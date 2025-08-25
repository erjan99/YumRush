from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .models import Order, Cart


class OrderRateAPIView(APIView):
    def post(self, request, pk):
        try:
            order = Order.objects.get(id=pk)
        except Order.DoesNotExist:
            return Response({"error": "Заказ не найден"}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderRatingSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "Рейтинг выставлен", "rating": order.rating})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CreateOrderView(APIView):
    @swagger_auto_schema(
        operation_description="Create order from cart with delivery information",
        request_body=CreateOrderSerializer,
        responses={
            201: OrderSerializer,
            400: "Bad request - validation errors",
            401: "Authentication required",
            404: "Cart not found or empty"
        }
    )
    def post(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

        # Получаем активную корзину пользователя
        try:
            cart = Cart.objects.get(user=request.user, is_active=True)
            if not cart.items.exists():
                return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)
        except Cart.DoesNotExist:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CreateOrderSerializer(data=request.data)
        if serializer.is_valid():
            # Создаем заказ
            order = Order.objects.create(
                user=request.user,
                total_price=sum(item.total_price for item in cart.items.all()),
                status='pending'
            )

            # Переносим товары из корзины в заказ
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity
                )

            # Создаем информацию о доставке
            delivery_data = serializer.validated_data
            Delivery.objects.create(
                order=order,
                delivery_type=delivery_data['delivery_type'],
                receiver_name=delivery_data['receiver_name'],
                receiver_phone_number=delivery_data['receiver_phone_number'],
                delivery_address=delivery_data.get('delivery_address', ''),
                description=delivery_data.get('description', ''),
                is_free_delivery=delivery_data.get('is_free_delivery', False)
            )

            # Очищаем корзину
            cart.items.all().delete()
            cart.is_active = False
            cart.save()

            # Возвращаем созданный заказ
            order_serializer = OrderSerializer(order)
            return Response(order_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)