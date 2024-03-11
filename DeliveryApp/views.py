from datetime import datetime

from django.db.models import Sum, Count
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated

from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes

from DeliveryApp.models import MenuItem, Category, Cart, Order, OrderItem
from DeliveryApp.serializers import MenuSerializer, CategorySerializer, CartSerializer, Order_Serializer, \
    OrderSerializer
@api_view(['GET','POST'])
def category_api(request):
    if request.method=='GET':
        category=Category.objects.all()
        serializer_item = CategorySerializer(category,many=True)
        return Response(serializer_item.data,status=status.HTTP_200_OK)
    if request.method=='POST':
            serializer_item = CategorySerializer(data=request.data,many=True)
            serializer_item.is_valid(raise_exception=True)
            serializer_item.save()
            return Response(serializer_item.data, status=status.HTTP_200_OK)
@api_view(['GET','POST'])
# @permission_classes(([IsAuthenticated]))
def menu_api(request):
    if request.method=='GET':
        menu=MenuItem.objects.all()
        price = request.query_params.get('price')
        category = request.query_params.get('category')
        search = request.query_params.get('search')
        ordering = request.query_params.get('ordering')
        if search:
            menu = menu.filter(title__icontains=search)
        if ordering:
                ordering_fields=ordering.split(",")
                # For giving multiple ordering fields
                #Ex- ordering=price,title
                menu=menu.order_by(*ordering_fields)
        # asterisk(*) operator is often used for unpacking iterable objects like lists, tuples etc.
        if price:
            price = price.split(",")
            menu = menu.filter(price__gte=price[0])
            if len(price)>1:
                menu=menu.filter(price__lte=price[1])
        if category:
            menu=menu.filter(category__title__iexact=category)
            # double underscore(category__title) is used for related field
        serializer_item = MenuSerializer(menu,many=True)
        return Response(serializer_item.data,status=status.HTTP_200_OK)
    elif request.method=='POST':
        if request.user.groups.filter(name="Manager").exists():
            serializer_item = MenuSerializer(data=request.data,many=True)
            serializer_item.is_valid(raise_exception=True)
            serializer_item.save()
            return Response(serializer_item.data, status=status.HTTP_201_CREATED)
        else:
            return Response("Access Denied", status=status.HTTP_401_UNAUTHORIZED)
@api_view(['GET','PUT','PATCH','DELETE'])
# @permission_classes(([IsAuthenticated]))
def single_menu_item(request,id):
    menu = get_object_or_404(MenuItem, pk=id)
    if request.method=='GET':
        serializer_item = MenuSerializer(menu)
        return Response(serializer_item.data)
    if request.user.groups.filter(name="Manager").exists():
        if request.method=='PATCH':
            serializer_item = MenuSerializer(menu,data=request.data,partial=True)
            serializer_item.is_valid(raise_exception=True)
            serializer_item.save()
            return Response(serializer_item.data, status=status.HTTP_201_CREATED)
        if request.method=='PUT':
            serializer_item = MenuSerializer(menu, data=request.data,partial=False)
            serializer_item.is_valid(raise_exception=True)
            serializer_item.save()
            return Response(serializer_item.data, status=status.HTTP_201_CREATED)
        if request.method=='DELETE':
            menu.delete()
            return Response(status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
from rest_framework.authtoken.admin import User
@api_view(['GET','POST','DELETE'])
# @permission_classes(([IsAuthenticated]))
def cart_item(request):
    if request.method=='GET':
        cart = Cart.objects.filter(user=request.user)
        serializer_item = CartSerializer(cart,many=True)
        return Response(serializer_item.data, status=status.HTTP_200_OK)
    if request.method=='POST':
        # dict={'user_id':request.user.id}
        # request.data.update(dict)
        serializer_item = CartSerializer(data=request.data,context={'request': request})
        serializer_item.is_valid(raise_exception=True)
        serializer_item.save()
        return Response(serializer_item.data, status=status.HTTP_201_CREATED)
    if request.method=='DELETE':
        cart = Cart.objects.filter(user=request.user)
        cart.delete()
        return Response(status=status.HTTP_200_OK)

@api_view(['GET','POST', 'DELETE'])
def Order_items(request):
    if request.method=='GET':
        if request.user.groups.filter(name="Manager").exists():
            order = OrderItem.objects.all()
            order = OrderSerializer(order, many=True)
            return Response(order.data, status=status.HTTP_201_CREATED)
        elif request.user.groups.filter(name="Delivery crew").exists():
            order=OrderItem.objects.filter(order__in=Order.objects.filter(delivery_crew_id=request.user.id))
            if order.exists():
                order = OrderSerializer(order, many=True)
                return Response(order.data, status=status.HTTP_201_CREATED)
            else:
                return Response("No order assigned", status=status.HTTP_201_CREATED)
        else:
            order=OrderItem.objects.filter(order__in=Order.objects.filter(user_id=request.user.id))
            order=OrderSerializer(order,many=True)
            return Response(order.data, status=status.HTTP_201_CREATED)
    if not request.user.groups.exists():
        if request.method=='POST':
            order_sum = Cart.objects.filter(user=request.user).aggregate(Sum('price'))
            last_order = Order.objects.last()
            if last_order is not None:
                id = last_order.id + 1
            else:
                id = 1
            order_data = {
                "id":id,
                "user": request.user.id,
                "total":format(order_sum['price__sum'], ".2f"),
                "date":datetime.today().date()
            }
            serializer_item = Order_Serializer(data=order_data)
            serializer_item.is_valid(raise_exception=True)
            serializer_item.save()
            order=Cart.objects.filter(user=request.user)
            serializer_item=CartSerializer(order,many=True)
            serializer_item = OrderSerializer(data=serializer_item.data, many=True,context={'id':id})
            serializer_item.is_valid(raise_exception=True)
            serializer_item.save()
            return Response(serializer_item.data, status=status.HTTP_201_CREATED)
    else:
        return Response("Access Denied", status=status.HTTP_401_UNAUTHORIZED)
@api_view(['GET','POST', 'DELETE'])
def order(request,id):
    if request.method=="GET":
        order= Order.objects.filter(user_id=request.user.id, id=id)
        if order:
            order = OrderItem.objects.filter(order__in=order)
            order=OrderSerializer(order,many=True)
            return Response(order.data,status.HTTP_200_OK)
        else:
            return Response("Order doesn't exist", status.HTTP_200_OK)
    if request.method=="PATCH":
        order = Order.objects.filter(user_id=request.user.id, id=id)
        order=Order_Serializer(order,data=request.data,partial=True)
        order.is_valid(raise_exception=True)
        order.save()
        return Response(status=status.HTTP_200_OK)
    if request.method=="DELETE":
        order=Order.objects.filter(user=request.user,id=id)
        order.delete()
        return Response(status=status.HTTP_200_OK)






