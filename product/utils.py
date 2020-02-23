import random
import string
import os
from django.utils.text import slugify


def get_filename_ext(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    return name, ext


def upload_image_path(instance, filename):
    new_filename = random.randint(1, 3910209312)
    name, ext = get_filename_ext(filename)
    final_filename = '{new_filename}{ext}'.format(new_filename=new_filename, ext=ext)
    return f"products/{slugify(instance.slug)}/{final_filename}"


def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def unique_slug_generator(instance, new_slug=None):

    if new_slug is not None:
        slug = new_slug
    else:
        slug = slugify(instance.name)

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(slug=slug).exists()
    if qs_exists:
        new_slug = f"{slug}-{random_string_generator(size=4)}"
        return unique_slug_generator(instance, new_slug=new_slug)
    return slug


def request_get_param(request):
    get_dict_copy = request.GET.copy()
    get_dict_copy.pop('page', True)
    return get_dict_copy.urlencode()


def comment_is_access(request, product):
    if request.user.is_authenticated:
        qs = product.comments.all().filter(author=request.user)
        if qs.count() == 0:
            return True
        else:
            return False
    else:
        return False
