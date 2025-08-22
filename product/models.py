from django.contrib.auth import get_user_model
from django.db import models


user = get_user_model()


#PRODUCT RELATED MODELS
class Category(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    image = models.FileField(upload_to='categories/', null=True, blank=True)

    def __str__(self):
        # Показываем полный путь: "Еда > Фрукты > Яблоки"
        if self.parent:
            return f"{self.parent} > {self.name}"
        return self.name


class Company(models.Model):
    name = models.CharField(max_length=255)
    logo = models.FileField(upload_to='companies/', null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    rating = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.FileField(upload_to='products/')
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    ingredients = models.TextField(null=True, blank=True)
    rating = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='products', null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def final_price(self):
        return self.discounted_price if self.discounted_price else self.original_price
