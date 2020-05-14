"""Backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from api.views import ProductsListView
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.authtoken.views import obtain_auth_token
from api.views import CustomObtainAuthToken,buy_products, ship, add_comment,registration_view, url_filters_cleaner, get_color_choices, ProductsFilterListView,filters_params_view, detail_view, add_item_cart_view, remove_item_cart_view, set_cart_view


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/prodlist/', ProductsListView.as_view()),
    path('token-auth/', CustomObtainAuthToken.as_view(), name='api_token_auth'),
    path('productfilterlist/', ProductsFilterListView.as_view(), name='filter_list'),
    path('filtersparams/', filters_params_view, name='filters'),
    path('url_filters_cleaner/', url_filters_cleaner, name='url_filters_leaner'),
    path('color-choices/', get_color_choices, name='color_choices'),
    path('registration/', registration_view, name='registration'),
    path('add_comment/', add_comment, name='add_comment'),
    path('buy_products/', buy_products, name='buy_products'),
    path('ships/', ship, name='ship'),

    path('cart/add_item/', add_item_cart_view, name='add_item'),
    path('cart/remove_item/', remove_item_cart_view, name='remove_item'),
    path('cart/set_cart/', set_cart_view, name='cart_item'),
    path('product/<slug:slug>/', detail_view, name='detail-view'),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)