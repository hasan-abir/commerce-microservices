from django.db import models
from time import timezone
import random
import string

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
    contact_email = models.EmailField()
    total = models.PositiveIntegerField()
    payment_intent_id = models.CharField(max_length=50, unique=True)

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
    item_id = models.PositiveIntegerField(unique=True)
    quantity = models.PositiveIntegerField()
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-item_id']

    def __str__(self):
        return f"Order item: {self.item_id}"