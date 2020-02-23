from rest_framework.generics import ListAPIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .serializer import CustomAuthTokenSerializer
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import render, get_object_or_404
from product.models import Product, Comment
from .models import CustomUser
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import facebook
from cart.serializer import CartSerializer
from cart.models import Item
import json
from .utils import update_cart
from product.serializers import CommentSerializer, ProductSerializer
from rest_framework import status
from django.http import Http404
from django.db.models import Q
from operator import __or__ as OR
from functools import reduce
from rest_framework.permissions import AllowAny, IsAuthenticated
from .pagination import SetPagination

@api_view(['GET', 'POST'])
def detail_view(request, slug):
    print(request.headers)
    product = get_object_or_404(Product, slug=slug)
    prod_serializer = ProductSerializer(product)
    comments = []
    for comm in list(product.comment.all()):
        comments.append(CommentSerializer(comm).data)
    return Response({"product_info": prod_serializer.data, "comments": comments})


@api_view(['GET', 'POST'])
def set_cart_view(request):

    if request.user.is_authenticated:
        cart = CartSerializer(request.user.cart).data
    elif request.data:

        cart = {'items': [], 'total': 0}
        for key, value in request.data.items():
            cart['items'].append({'product': ProductSerializer(Product.objects.get(id=key)).data, 'quantity': value})
    return Response(cart)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def buy_products(request):
    data = request.data
    for prod in data['products']:
        product = Product.objects.get(id=prod['id'])
        product.sell_quantity += prod['quantity']
        product.customers.add(request.user)
        product.save()
    request.user.cart.items.all().delete()
    return Response({"message": "Pomyślnie zakupiłeś produkty."})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_comment(request):
    data = request.data
    comment = Comment(content=data['comment'], author=request.user, product=Product.objects.get(id=data['id']), rating=data['rate'])
    comment.save()
    return Response({'new_comment': CommentSerializer(comment).data})


@api_view(['POST', 'GET'])
def filters_params_view(request):
    filterType = request.GET.get('filterType', None)
    priceRange = Product.objects.get_min_max_category_price(filterType)
    return Response({'price': priceRange})



@api_view(['GET'])
def get_color_choices(request):
    return Response(Product.objects.get_color_choices())


@api_view(['POST', 'GET'])
def url_filters_cleaner(request):

    url_filters = request.data

    def isDouble(x):
        return url_filters[x][0] if isinstance(url_filters[x], list) else url_filters[x]

    clean_params = {
        'category': '',
        'page': 1,
        'order': '',
        'price_from': '',
        'price_to': '',
        'colors': '',
        'cloth': '',
    }
    category = url_filters.get("category", None)

    queryset = Product.objects.filter(category=category)

    if queryset:
        print(request.data)
        clean_params['category'] = category
        if url_filters.get('page', None):
            page = isDouble('page')
            try:
                if int(page) >= 0 and int(page) < 100:
                    clean_params['page'] = page
            except ValueError:
                print('Except')
        minmax_price = Product.objects.get_min_max_category_price(category)
        min_price = int(minmax_price[0])
        max_price = int(minmax_price[1])
        if url_filters.get('order', None):
            order = isDouble('order')
            if order in Product.objects.get_order_options().keys():
                clean_params['order'] = order
        if url_filters.get('price_from', None):

            price_from = isDouble('price_from')
            try:
                price_from = int(price_from)
                if int(price_from) < min_price:
                    clean_params['price_from'] = min_price
                elif int(price_from) <= max_price:
                    clean_params['price_from'] = int(price_from)
                else:
                    clean_params['price_from'] = max_price
            except ValueError:
                print('Except')
        if url_filters.get('price_to', None):
            price_to = isDouble('price_to')
            try:
                price_to = int(price_to)
                if clean_params['price_from'] and price_to < clean_params['price_from']:
                    clean_params['price_to'] = clean_params['price_from'] + 1
                elif price_to < min_price:
                    clean_params['price_to'] = min_price
                elif price_to <= max_price:
                    clean_params['price_to'] = price_to
                else:
                    clean_params['price_to'] = max_price
            except ValueError:
                print('Except')
        if url_filters.get('colors', None):
            colors = isDouble('colors').split(',')
            clean_colors = []
            for color in colors:
                if Product.objects.filter(color=color) and color not in clean_colors:
                    clean_colors.append(color)
            clean_params['colors'] = ','.join(clean_colors)
        if url_filters.get('cloth', None):
            cloth = isDouble('cloth')
            if Product.objects.filter(cloth=cloth):
                clean_params['cloth'] = cloth
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)
    return Response({'clean_params': clean_params, 'price_range': minmax_price, 'allColors': Product.objects.get_color_choices()})


@api_view(['POST', 'GET'])
def add_item_cart_view(request):
    prod_id = request.data.get('id', None)
    dat = CartSerializer(request.user.cart)

    if prod_id is not None:
        for item in request.user.cart.items.all():
            if item.product.id == prod_id:
                item.quantity += 1
                item.save()
                cart = CartSerializer(request.user.cart)
                return Response(cart.data)
        new_prod = Product.objects.filter(id=prod_id).first()
        new_item = Item(product=new_prod, cart=request.user.cart)
        new_item.save()
        cart = CartSerializer(request.user.cart)
        return Response(cart.data)

    return Response({'chuj': 'takkk'})


@api_view(['POST'])
def remove_item_cart_view(request):
    prod_id = request.data.get('id', None)
    removeAll = request.data.get('all', None)

    if prod_id is not None:
        for item in request.user.cart.items.all():
            if item.product.id == prod_id:
                if removeAll:
                    item.delete()
                    return Response({'all': 'ttue'})
                if item.quantity == 1:
                    item.delete()
                else:
                    item.quantity -= 1
                    item.save()
                return Response({'all': 'false'})

    return Response({'chuj': 'takkk'})


class ProductsListView(ListAPIView):

    pagination_class = SetPagination
    serializer_class = ProductSerializer

    def get_queryset(self):
        param = self.request.GET.get('filter')
        print(param)
        if param == 'rating':
            return Product.objects.all().order_by('-average_rating')
        if param == 'sell':
            return Product.objects.all().order_by('-sell_quantity')
        return Product.objects.all()


class ProductsFilterListView(ListAPIView):

    serializer_class = ProductSerializer

    def get_queryset(self):

        params = self.request.GET

        category = params.get("category", None)
        price_from = params.get("price_from", None)
        price_to = params.get("price_to", None)
        cloth = params.get('cloth', None)
        colors = params.get('colors', None)
        order = params.get('order', None)

        queryset = Product.objects.filter(category=category)

        if queryset:
            try:
                if price_from:
                    queryset = queryset.filter(price__gte=int(price_from))
                if price_to:
                    queryset = queryset.filter(price__lte=int(price_to))
            except ValueError:
                print('Except')
            if colors:
                queryset = queryset.filter(reduce(OR, (Q(color=color) for color in colors.split(','))))
            if cloth:
                queryset = queryset.filter(cloth=cloth)
            if order in Product.objects.get_order_options().keys():
                queryset = queryset.order_by(Product.objects.get_order_options()[order])
        else:
            raise Http404
        return queryset


class CustomObtainAuthToken(ObtainAuthToken):
    permission_classes = [AllowAny]
    serializer_class = CustomAuthTokenSerializer

    def post(self, request, *args, **kwargs):

        old_cart = request.data['old_cart']
        serializer = self.serializer_class(data={"username": request.data['username'],
                                                 'password': request.data['password']},
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        if old_cart:
            update_cart(user.cart, old_cart)
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user_info': {'username': user.username, 'email': user.email, 'image': user.profile_image.url}})


@api_view(['POST'])
def registration_view(request):
    data = request.data
    errors = {}
    if CustomUser.objects.filter(username=data.username):
        errors['username'] = 'Taka nazwa użytkownika juz istnieje.'
    if CustomUser.objects.filter(email=data.email):
        errors['email'] = 'Taki adres email już istnieje.'
    if not errors:
        user = CustomUser(username=data.username, email=data.email, password=data.password)
        user.save()
        return Response({'message': 'Konto zostało utworzone'})
    else:
        return Response({})


@csrf_exempt
def facebook_login_view(request):

    data = json.loads(request.body.decode('utf-8'))
    access_token = data.get('accessToken')
    old_cart = data.get('old_cart', None)
    new_user = False
    try:
        graph = facebook.GraphAPI(access_token=access_token)
        user_info = graph.get_object(
            id='me',
            fields='first_name, middle_name, last_name, id, '
            'currency, hometown, location, locale, '
            'email, gender, interested_in, picture.type(large),'
            ' birthday, cover')
    except facebook.GraphAPIError:
        return JsonResponse({'error': 'Invalid data'}, safe=False)

    try:
        user = CustomUser.objects.get(facebook_id=user_info.get('id'))

    except CustomUser.DoesNotExist:
        password = CustomUser.objects.make_random_password()
        user = CustomUser(
            first_name=user_info.get('first_name'),
            last_name=user_info.get('last_name'),
            email=user_info.get('email'),

            facebook_id=user_info.get('id'),
            profile_image=user_info.get('picture')['data']['url'],
            date_joined=datetime.now(),
            username=user_info.get('email') or user_info.get('last_name'),
            gender=user_info.get('gender'),
            is_active=1)
        user.set_password(password)
        user.save()
        new_user = True
    if old_cart:
        update_cart(user.cart, old_cart)
    token = Token.objects.get(user=user).key
    if token:
        return JsonResponse({'auth_token': token, 'user_info': {'username': user.first_name, 'email': user.email, 'image': user.profile_image}},
                            safe=False)
    else:
        return JsonResponse({'error': 'Invalid data'}, safe=False)