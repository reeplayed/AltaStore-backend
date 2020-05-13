from .utils import unique_slug_generator, upload_image_path
from django.db import models
from django.db.models.signals import pre_save, post_save
from decimal import Decimal
from django.conf import settings

COLOR = (
    ('white', '#FEFEFE'),
    ("green", '#3FA434'),
    ("black", '#010500'),
    ("grey", '#9C9E9C'),
    ("other", '#D0D1D0')
)
CATEGORY =(
    ('narozniki', 'Narożniki'),
    ('sofy', 'Sofy'),
    ('fotele', 'Fotele')
)

CLOTH = (
    ('leather', 'Leather'),
    ('cotton', 'Cotton')
)


class ProductManager(models.Manager):

    def get_order_options(self):

        options = {
            'price_up': '-price',
            'price_down': 'price',
            'rate_up': '-rate',
            'rate_down': 'rate'
        }
        return options

    def get_min_max_category_price(self, category):
        min = Product.objects.filter(category=category).order_by('price').first().price
        max = Product.objects.filter(category=category).order_by('-price').first().price
        return [int(min), int(max)]

    def get_color_choices(self):
        return COLOR


class Product(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(null=True, blank=True, unique=True)
    content = models.TextField()
    date_add = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)

    image = models.ImageField(default='default.jpg', upload_to=upload_image_path)
    image_2 = models.ImageField(default='default.jpg', upload_to=upload_image_path)
    image_3 = models.ImageField(default='default.jpg', upload_to=upload_image_path)
    price = models.DecimalField(default=11.00, max_digits=9, decimal_places=2)
    category = models.CharField(max_length=50, null=True, blank=True, choices=CATEGORY)
    color = models.CharField(max_length=10, null=True, blank=True, choices=COLOR)
    cloth = models.CharField(max_length=10, null=True, blank=True, choices=CLOTH)
    average_rating = models.DecimalField(default=0.00, max_digits=9, decimal_places=2)
    sell_quantity = models.IntegerField(default=0)
    customers = models.ManyToManyField(settings.AUTH_USER_MODEL, null=True, blank=True)

    objects = ProductManager()

    def get_absolute_url(self):
        return f'product/{self.slug}'

    def __str__(self):
        return self.name


def product_pre_save_receiver(sender, instance, *args, **kwargs):
    if instance.slug is None:
         instance.slug = unique_slug_generator(instance)


pre_save.connect(product_pre_save_receiver, sender=Product)


class Comment(models.Model):
    content = models.TextField(default="Świetny produkt. Polecam !!!")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='author', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='comment', on_delete=models.CASCADE)
    rating = models.DecimalField(max_digits=9, decimal_places=2)

    def __str__(self):
        return f'Comment nr {self.id}'


def set_average_rating(sender, instance, created, *args, **kwargs):
    all_rates = instance.product.comment.all()
    quantity = 0
    rates_total = 0
    for rate in all_rates:
        quantity += 1
        rates_total += rate.rating
    prod = instance.product
    prod.average_rating = round(Decimal(rates_total/quantity), 2)
    prod.save()


post_save.connect(set_average_rating, sender=Comment)
