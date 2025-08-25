
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .models import Order, Cart


class OrderRateView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Rate a delivered order",
        request_body=OrderRatingSerializer,
        responses={
            200: "Rating successfully added",
            400: "Bad request - order not delivered or validation errors",
            404: "Order not found",
            401: "Authentication required"
        }
    )
    def post(self, request, pk):
        try:
            order = Order.objects.get(id=pk, user=request.user)
        except Order.DoesNotExist:
            return Response({"error": "Заказ не найден"}, status=status.HTTP_404_NOT_FOUND)

        # Проверяем, что заказ можно оценить
        if order.status != 'delivered':
            return Response({
                "error": "Можно оценить только доставленные заказы"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Проверяем, что заказ еще не оценен
        if order.rating:
            return Response({
                "error": "Заказ уже оценен"
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = OrderRatingSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": "Рейтинг выставлен",
                "rating": order.rating
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserOrderHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get user's order history",
        responses={
            200: UserOrderHistorySerializer(many=True),
            401: "Authentication required"
        }
    )
    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        serializer = UserOrderHistorySerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CourierOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get all orders for courier",
        responses={
            200: OrderSerializer(many=True),
            403: "Permission denied - not a courier",
            401: "Authentication required"
        }
    )
    def get(self, request):
        if request.user.role != 'courier':
            return Response({
                "error": "Недостаточно прав. Только курьеры могут просматривать заказы"
            }, status=status.HTTP_403_FORBIDDEN)

        orders = Order.objects.all().order_by('-created_at')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateOrderView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Create order from cart with delivery information",
        request_body=CreateOrderSerializer,
        responses={
            201: OrderSerializer,
            400: "Bad request - validation errors or empty cart",
            401: "Authentication required",
            404: "Cart not found"
        }
    )
    def post(self, request):
        # Получаем активную корзину пользователя
        try:
            cart = Cart.objects.get(user=request.user, is_active=True)
            if not cart.items.exists():
                return Response({
                    'error': 'Корзина пуста'
                }, status=status.HTTP_400_BAD_REQUEST)
        except Cart.DoesNotExist:
            return Response({
                'error': 'Корзина не найдена'
            }, status=status.HTTP_404_NOT_FOUND)

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