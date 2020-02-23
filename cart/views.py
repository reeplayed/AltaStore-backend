from django.shortcuts import render
from .serializer import ProductSerializer
from rest_framework.generics import ListAPIView
from product.models import Product
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .serializer import CustomAuthTokenSerializer
from rest_framework.decorators import api_view
from django.shortcuts import render, get_object_or_404
from product.models import Product

from .models import CustomUser
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import facebook

import json