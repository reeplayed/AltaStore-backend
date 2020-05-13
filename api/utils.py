from cart.models import Item
from product.models import Product
import random


def update_cart(userCart, old_cart):

    for key, value in old_cart.items():
        product = Product.objects.get(id=key)
        item = Item.objects.filter(product=product, cart=userCart).first()
        print(product,item)
        if item:
            item.quantity += value
            item.save()
        else:
            Item.objects.create(product=product, cart=userCart, quantity=value)


def set_random_image():
    images = ['default.jpg', 'joda.jpeg', 'wiedzmin.jpeg']
    return random.choice(images)




