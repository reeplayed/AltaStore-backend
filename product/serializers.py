from rest_framework import serializers
from api.serializer import CustomUserSerializer
from .models import Product, Comment

class CommentSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer()

    class Meta:
        model = Comment
        fields = ['id', 'content', 'rating', 'author']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'card_image', 'price', 'average_rating']

class ProductSerializerExpand(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'content', 'image', 'image_2', 'image_3', 'price', 'average_rating']