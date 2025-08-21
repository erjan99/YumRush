from django.contrib import admin
from .models import *

admin.site.register(Category)
admin.site.register(Cart)
admin.site.register(Product)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Delivery)
admin.site.register(Company)
# Register your models here.
