from rest_framework.generics import ListAPIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .serializer import CustomAuthTokenSerializer
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import render, get_object_or_404
from product.models import Product, Comment
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import facebook
from cart.serializer import CartSerializer
from cart.models import Item
import json
from .utils import update_cart
from product.serializers import CommentSerializer, ProductSerializer, ProductSerializerExpand
from rest_framework import status
from django.http import Http404
from django.db.models import Q
from operator import __or__ as OR
from functools import reduce
from rest_framework.permissions import AllowAny, IsAuthenticated
from .pagination import SetPagination
import random 
from django.conf import settings

@api_view(['POST'])
def ship(request):
    
    ships = [5, 4, 3, 3,5, 2, 2, 2]

    output_choices = []

    output_borders = {}

    ships_dementions = {}

    scope = [i for i in range(0, 10)]

    all = []

    for i in scope:
        for j in scope:
            all.append([i,j])

    directions = [(0,1), (0, -1), (1, 0), (-1, 0)]

    def valid(array, all, choices):
            for element in array:
                if (element not in all) or (element in choices):
                    return False
            return True

    border = []
    choices = []

    index = 1

    for length in ships:

        isFind = False

        repeatings = []

        cyclic_border = []

        cyclic_choice = []

        while not isFind:
            rand = random.choice(all) # all-choices-border
           
            random.shuffle(directions)

            for dir in directions:

                drct = [ [rand[0]+i*dir[0], rand[1]+i*dir[1]] for i in range(1, length+1)]
                
                if valid(drct, all, choices+border):
                    
                    ships_dementions[f'ship{index}'] = length

                    choices += drct
                    output_choices += [ { 'idx':(i[0]*len(scope)+i[1]), 'name': f'ship{index}', 'hit': False} for i in drct]

                    cyclic_border.append([  drct[0][0]-dir[0] , drct[0][1]-dir[1]       ])
                    cyclic_border.append([  drct[len(drct)-1][0]+dir[0] , drct[len(drct)-1][1]+dir[1]       ])
                    
                    for item in range(-1,len(drct)+1):
                        cyclic_border.append([      rand[0]+dir[1]+dir[0]*(item+1), rand[1]+dir[0]+dir[1]*(item+1)    ])
                        cyclic_border.append([      rand[0]-dir[1]+dir[0]*(item+1), rand[1]-dir[0]+dir[1]*(item+1)    ])
                    
                    output_borders[f'ship{index}'] = []
                    
                    for i in cyclic_border:
                        if (i[0] in scope) and (i[1] in scope):
                            output_borders[f'ship{index}'].append((i[0]*len(scope)) + i[1])


                    index += 1

                    border += cyclic_border
                    isFind = True
                    break
            repeatings.append(rand)

    randoms = [ (i[0]*len(scope))+i[1] for i in choices]
    
    final_output = []

    for i in range(0,100):
        if i not in randoms:
            final_output.append({'idx': i, 'name': '', 'hit': False})
       
    final_output += output_choices

    final_output = sorted(final_output, key = lambda i: (i['idx'])) 

    # all = [ i[0]*10+i[1] for i in all]
    # randoms = [ (i[0]*len(scope))+i[1] for i in choices]
    # border = [ ((i[0]*len(scope)) if i[0] in scope else 1000) + (i[1] if i[1] in scope else 1000) for i in border]

    res = {
        'array' : final_output,
        'ships': ships_dementions,
        'border': output_borders
    }

    return Response(res)
    

@api_view(['GET', 'POST'])
def detail_view(request, slug):
    print(request.headers)
    product = get_object_or_404(Product, slug=slug)
    prod_serializer = ProductSerializerExpand(product)
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
    if settings.AUTH_USER_MODEL.objects.filter(username=data['username']):
        errors['username'] = 'Taka nazwa użytkownika juz istnieje.'
    if settings.AUTH_USER_MODEL.objects.filter(email=data['email']):
        errors['email'] = 'Taki adres email już istnieje.'
    if not errors:
        user = settings.AUTH_USER_MODEL(username=data['username'], email=data['email'], password=data['password'])
        user.save()
        return Response({'message': 'Konto zostało utworzone.'})
    else:
        raise Http404


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
        user = settings.AUTH_USER_MODEL.objects.get(facebook_id=user_info.get('id'))

    except settings.AUTH_USER_MODEL.DoesNotExist:
        password = settings.AUTH_USER_MODEL.objects.make_random_password()
        user = settings.AUTH_USER_MODEL(
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