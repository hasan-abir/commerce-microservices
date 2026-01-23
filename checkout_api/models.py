from django.db import models
from time import timezone
import random
import string

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    is_active = models.BooleanField()

    class Meta:
        ordering = ['-price']

    def __str__(self):
        return self.name

class Cart(models.Model):
    ACTIVE = "ACT"
    PROCESSING = "PRO"
    COMPLETED = "COM"
    FAILED = "FAI"
    STATUS_CHOICES = {
        ACTIVE: "Active",
        PROCESSING: "Processing",
        COMPLETED: "Completed",
        FAILED: "Failed"
    }

    session_key = models.CharField(max_length=50, unique=True)
    status = models.CharField(choices=STATUS_CHOICES, max_length=3, default=ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"User: {self.session_key}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    class Meta:
        ordering = ['-quantity']
        constraints = [
            models.UniqueConstraint(
                fields=['cart', 'product'], 
                name='unique_cart_product'
            )
        ]

    def __str__(self):
        return f"Belongs to cart: {self.cart.session_key}"
    
def generate_order_number():
    prefix = 'ORD-'
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return prefix + suffix
    
class Order(models.Model):
    PENDING = "PN"
    PAID = "PD"
    SHIPPED = "SH"
    CANCELLED = "CN"
    STATUS_CHOICES = {
        PENDING: "Pending",
        PAID: "Paid",
        SHIPPED: "Shipped",
        CANCELLED: "Cancelled",
    }

    order_number = models.CharField(max_length=20, unique=True, editable=False, blank=True)
    status = models.CharField(
        max_length=2,
        choices=STATUS_CHOICES,
        default=PENDING,
    )
    date_placed = models.DateTimeField(auto_now=True)
    source_cart_session_key = models.CharField(max_length=50)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=3)
    contact_email = models.EmailField()
    shipping_address_line1	= models.CharField(max_length=100)
    shipping_city = models.CharField(max_length=100)
    shipping_country = models.CharField(max_length=100)
    shipping_zip = models.CharField(max_length=100)

    class Meta:
        ordering = ['-date_placed']

    def save(self, **kwargs):
        if not self.order_number:
            is_unique = False
            while not is_unique:
                new_number = generate_order_number()
                if not Order.objects.filter(order_number=new_number).exists():
                    self.order_number = new_number
                    is_unique = True
        
        super().save(**kwargs)

    def __str__(self):
        return f"Order number: {self.order_number}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    original_product_id = models.IntegerField()
    product_name = models.CharField(max_length=100)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"Order item for order: {self.order.order_number}"