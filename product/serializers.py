from rest_framework import serializers
from .models import *


class CategoryListSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)
    class Meta:
        model = Category
        fields = ['id', 'name', 'image']

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'logo']


class ProductListSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)
    category = CategoryListSerializer()
    company = CompanySerializer()

    class Meta:
        model = Product
        fields = ['id', 'name', 'image', 'original_price', 'discounted_price', 'category', 'rating', 'company', 'grams']


class ProductDetailSerializer(serializers.ModelSerializer):
    company = CompanySerializer()
    class Meta:
        model = Product
        fields = ['id', 'name', 'original_price', 'discounted_price', 'category', 'rating', 'company', 'description', 'image', 'ingredients', 'grams']
