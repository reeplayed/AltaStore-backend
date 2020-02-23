from rest_framework import serializers
from .models import Cart, Item
from product.serializers import ProductSerializer


class ItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = Item
        fields = ['quantity', 'product']


class CartSerializer(serializers.ModelSerializer):
    items = ItemSerializer(many=True)

    class Meta:
        model = Cart
        fields = ['items', 'total']

