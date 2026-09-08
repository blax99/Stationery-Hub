from rest_framework import serializers
from .models import Category, Products


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description']
        read_only_fields = ['slug']


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )
    in_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Products
        fields = [
            'id', 'name', 'slug', 'description', 'price',
            'stock', 'is_available', 'image', 'category',
            'category_id', 'in_stock', 'created_at', 'updated_at'
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at']