from _decimal import Decimal
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from DeliveryApp.models import MenuItem, Category, Cart, Order, OrderItem


class CategorySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(max_value=90)

    class Meta:
        model = Category
        fields = ['id', 'slug', 'title']
class MenuSerializer(serializers.ModelSerializer):
    price_after_tax = serializers.SerializerMethodField(method_name='PriceAfterTax')
    category_id = serializers.IntegerField(write_only=True, max_value=90)
    # max_value is for validating data that id cannot be more than 90
    category = CategorySerializer(read_only=True)
    # id = serializers.IntegerField(write_only=True)

    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'price', 'price_after_tax', 'category', 'category_id']
        extra_kwargs = {
            'price': {'min_value': 2, 'max_value': 500},
            'title': {
                # Sometimes API developers need to make sure that there is no duplicate entry made by the clients
                'validators': [
                    UniqueValidator(
                        queryset=MenuItem.objects.all()
                    )
                ]
            }
        }
        # Data Validation by extra_kwargs
    def PriceAfterTax(self, i: MenuItem):
        return i.price + i.price * Decimal(0.17)
class CartSerializer(serializers.ModelSerializer):
    menuitem_id=serializers.IntegerField()
    menu=serializers.SerializerMethodField(method_name='Menu')
    unit_price=serializers.SerializerMethodField(method_name='UnitPrice')
    price = serializers.SerializerMethodField(method_name='Price')
    class Meta:
        model = Cart
        fields = ['menuitem_id','menu','quantity','unit_price','price']

    def UnitPrice(self, i: Cart):
        return i.unit_price
    def Price(self, i: Cart):
        return i.price
    def Menu(self,i:Cart):
        return i.menuitem.title

    def create(self, validated_data):
        # Extract user_id from request context
        print(validated_data)
        user_id = self.context['request'].user.id
        validated_data['user_id'] = user_id
        menuitem=MenuItem.objects.get(id=validated_data['menuitem_id'])
        validated_data['unit_price'] = menuitem.price
        validated_data['price'] = menuitem.price*validated_data['quantity']
        return Cart.objects.create(**validated_data)
    # Similar to create there are update and save functions also when we don't define them they work as default
    # These function we generally define when we want customization


class Order_Serializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    class Meta:
        model=Order
        fields='__all__'
class OrderSerializer(serializers.ModelSerializer):
    menuitem_id = serializers.IntegerField()
    menuitem = serializers.SerializerMethodField(method_name='Menu')
    unit_price = serializers.DecimalField(max_digits=6,decimal_places=2)
    price = serializers.DecimalField(max_digits=6,decimal_places=2)
    order=Order_Serializer(read_only=True)
    class Meta:
        model = OrderItem
        fields = ['order','menuitem_id','menuitem','quantity','unit_price','price']
    def Menu(self,i:Cart):
        return i.menuitem.title
    def create(self, validated_data):
        # Extract user_id from request context
        print(validated_data)
        order_id = self.context['id']
        validated_data['order'] = Order.objects.get(id=order_id)
        return OrderItem.objects.create(**validated_data)