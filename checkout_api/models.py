from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    is_active = models.BooleanField()

    def __str__(self):
        return self.name

class Cart(models.Model):
    session_key = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"User: {self.session_key}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return f"Belongs to cart: {self.cart.session_key}"
