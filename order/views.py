from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import OrderRatingSerializer, CartSerializer, UserOrderHistorySerializer
from .models import Order, Cart, user


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

# User's orders


class UserOrderHistoryView(APIView):
    def get(self, request):
        orders = Order.objects.filter(user=request.user)
        serializer = UserOrderHistorySerializer(orders, many=True)
        return Response(serializer.data)

# Courier's orders


class CourierOrdersView(APIView):
    def get(self, request):
        order = Order.objects.filter(user=request.user)
        if user.role != "courier":
            raise PermissionDenied("Доступ разрешен только курьерам!")
        return Order.filter(courier=user)
