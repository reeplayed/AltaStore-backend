from django.db import models
from django.conf import settings
from product.models import Product
from django.db.models.signals import pre_save, post_save, m2m_changed


class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    updatetime = models.DateTimeField(auto_now=True)
    addtime = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(default=0.00, max_digits=9, decimal_places=2)

    def __str__(self):
        return f'Card nr {self.id}'

    @property
    def count(self):
        return self.product.all().count()


class Item(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField(default=1)
    total = models.DecimalField(null=True, blank=True, max_digits=9, decimal_places=2)


def item_total(sender, instance, *args, **kwargs):
    instance.total = instance.product.price * instance.quantity


pre_save.connect(item_total, sender=Item)


def cart_total(sender, instance, created, *args, **kwargs):
    total = 0
    for i in instance.cart.items.all():
        total += i.total

    instance.cart.total = total
    instance.cart.save()


post_save.connect(cart_total, sender=Item)

def cart_create(sender, instance, created, *args, **kwargs):
    if created:
        Cart.objects.create(user=instance)


post_save.connect(cart_create, sender=settings.AUTH_USER_MODEL)

