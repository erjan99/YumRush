from django.contrib.auth import get_user_model
from django.db import models
from rest_framework.templatetags.rest_framework import items

user = get_user_model()

#PRODUCT RELATED MODELS
class Category(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    image = models.ImageField(upload_to='categories/', null=True, blank=True)

    def __str__(self):
        # Показываем полный путь: "Еда > Фрукты > Яблоки"
        if self.parent:
            return f"{self.parent} > {self.name}"
        return self.name


class Company(models.Model):
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='companies/', null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    rating = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='products/')
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    ingredients = models.TextField(null=True, blank=True)
    rating = models.DecimalField(max_digits=1, decimal_places=1, null=True, blank=True, default=0.0,)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='products', null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def final_price(self):
        return self.discounted_price if self.discounted_price else self.original_price



#ORDER RELATED MODELS

class Order(models.Model):
    user = models.ForeignKey(user, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='Pending')  # e.g., Pending, Shipped, Delivered, Cancelled
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Order {self.id} by {self.user.username} - Status: {self.status} - Total: ${self.total_price:.2f}"

    @property
    def calculated_total_price(self):
        return sum(item.total_price for item in self.items.all())


class Delivery(models.Model):
    DELIVERY_TYPE_CHOICES = [
        ('pickup', 'Pickup'),
        ('delivery', 'Delivery'),
    ]

    is_free_delivery = models.BooleanField(default=False)
    delivery_type = models.CharField(max_length=123,choices=DELIVERY_TYPE_CHOICES, default='pickup')
    delivery_address = models.CharField(max_length=255, null=True, blank=True)  # Optional field for delivery address
    description = models.TextField(null=True, blank=True)  # Optional field for additional delivery information
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='deliveries')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Delivery for Order {self.order.id} - {'Delivery' if self.delivery else 'Pickup'}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order: {self.order.id})"

    @property
    def total_price(self):
        return self.product.final_price * self.quantity



#CART MODELS

class Cart(models.Model):
    user = models.ForeignKey(user, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'Cart for {self.user.username}'


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return f'{self.product}({self.quantity})'

    @property
    def total_price(self):
        return self.product.final_price * self.quantity





