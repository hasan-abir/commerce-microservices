from rest_framework import serializers, validators
from checkout_api.models import Product, Cart, CartItem, Order, OrderItem, PaymentIntent
from decimal import *

class ProductSerializer(serializers.HyperlinkedModelSerializer):
    price = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=round(Decimal('0.01'), 2))
    stock = serializers.IntegerField(min_value=1)
    class Meta:
        model = Product
        fields = '__all__'

class CartSerializer(serializers.HyperlinkedModelSerializer):
    session_key = serializers.CharField(validators=[validators.UniqueValidator(queryset=Cart.objects.all(), message="Cart with this session key already exists.")])
    total = serializers.SerializerMethodField()
    subtotal = serializers.SerializerMethodField()
    class Meta:
        model = Cart
        fields = '__all__'

    def get_subtotal(self, obj) -> Decimal:
        cart_subtotal = 0

        cartItems = CartItem.objects.filter(cart=obj)

        for cartItem in cartItems:
            cart_subtotal += cartItem.product.price * cartItem.quantity

        cart_subtotal = Decimal(cart_subtotal)

        return cart_subtotal.quantize(Decimal("0.01"), rounding=ROUND_CEILING)
    
    def get_total(self, obj) -> Decimal:
        tax_rate = Decimal("0.08")
        cart_subtotal = self.get_subtotal(obj)

        cart_total = cart_subtotal + cart_subtotal * tax_rate

        cart_total = Decimal(cart_total)

        return cart_total.quantize(Decimal("0.01"), rounding=ROUND_CEILING)
    
class CartItemSerializer(serializers.HyperlinkedModelSerializer):
    quantity = serializers.IntegerField(min_value=1)
    cart = serializers.HyperlinkedRelatedField(
        view_name='cart-detail',
        queryset=Cart.objects.all(),
        required=False
    )

    class Meta:
        model = CartItem
        fields = '__all__'

        validators = [
            validators.UniqueTogetherValidator(
                queryset=CartItem.objects.all(),
                fields=['cart', 'product'],
                message="This product is already in the cart."
            )
        ]

class CartItemRequestSerializer(CartItemSerializer):
    class Meta(CartItemSerializer.Meta):
        fields = ['product', 'quantity']

class OrderSerializer(serializers.HyperlinkedModelSerializer):
    order_number = serializers.CharField(read_only=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0.01'))
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0.01'))
    tax_rate = serializers.DecimalField(max_digits=5, decimal_places=3, min_value=Decimal('0.01'))
    class Meta:
        model = Order
        fields = '__all__'

class OrderItemSerializer(serializers.HyperlinkedModelSerializer):
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=round(Decimal('0.01'), 2))
    quantity = serializers.IntegerField(min_value=1)
    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderDataSerializer(serializers.Serializer):
    contact_email = serializers.EmailField()
    shipping_address_line1 = serializers.CharField(max_length=100)
    shipping_zip = serializers.CharField(max_length=100)
    shipping_city = serializers.CharField(max_length=100)
    shipping_country = serializers.CharField(max_length=100)

class PaymentSerializer(serializers.Serializer):
    total = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0.01'))

class PaymentIntentSerializer(serializers.HyperlinkedModelSerializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0.01'))
    class Meta:
        model = PaymentIntent
        fields = '__all__'