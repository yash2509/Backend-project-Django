from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views, views
from rest_framework.authtoken.views import obtain_auth_token
app_name = 'DeliverApp'
urlpatterns = [
    path('api/menu_items',views.menu_api,name='menu'),
    path('api/menu_items/<int:id>',views.single_menu_item,name='menu'),
    path('api/cart/menu_items',views.cart_item,name='cart'),
    path('api/category',views.category_api,name='category'),
    path('api/order',views.Order_items,name='order'),
    path('api/order/<int:id>',views.order,name='order')
]

