from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from django.core import validators
from django.utils import timezone
from .utils import set_random_image

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager

from rest_framework.authtoken.models import Token


class CustomUser(AbstractBaseUser, PermissionsMixin):
   
    email = models.EmailField(
        ('email address'),
        unique=True,
        error_messages={
            'unique': ("A user with that email already exists."),
        })

    date_joined = models.DateTimeField(('date joined'), default=timezone.now)

    first_name = models.CharField(('first name'), max_length=30, null=True, blank=True)
    last_name = models.CharField(('last name'), max_length=50, null=True, blank=True)
    middle_name = models.CharField(
        max_length=64, verbose_name=('middle name'), null=True, blank=True)

    phone = models.CharField(max_length=64, verbose_name=('user phone'),null=True, blank=True)

    username = models.CharField(
        ('username'),
        max_length=100,
        unique=True,
        help_text=('Required. 30 characters or fewer. Letters, digits and '
                   '@/./+/-/_ only.'),
        validators=[
            validators.RegexValidator(
                r'^[\w.@+-]+$',
                ('Enter a valid username. '
                 'This value may contain only letters, numbers '
                 'and @/./+/-/_ characters.'), 'invalid'),
        ],
        error_messages={
            'unique': ("A user with that username already exists."),
        })
    is_staff = models.BooleanField(
        ('staff status'),
        default=False,
        help_text=('Designates whether the user can log into this admin '
                   'site.'))
    is_active = models.BooleanField(
        ('active'),
        default=True,
        help_text=('Designates whether this user should be treated as '
                   'active. Unselect this instead of deleting accounts.'))

    facebook_id = models.CharField(max_length=200, unique=True, null=True, blank=True)
    profile_image = models.ImageField(default=set_random_image())

    gender = models.CharField(max_length=10, null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        managed = True
        abstract = False
        db_table = 'auth_user'


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    Token.objects.get_or_create(user=instance)