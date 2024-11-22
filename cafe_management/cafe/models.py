from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    ROLE_CHOICES = (
        ('owner', 'Owner'),
        ('waiter', 'Waiter'),
        ('chef', 'Chef'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return self.user.username

class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.name

class Order(models.Model):
    waiter = models.ForeignKey(User, on_delete=models.CASCADE)
    table_number = models.IntegerField()
    customer_name = models.CharField(max_length=100)
    items = models.ManyToManyField(MenuItem, through='OrderItem')
    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)



class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

class ChefNotification(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    notified = models.BooleanField(default=False)

class Notification(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    waiter = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Notification for {self.waiter.username}: {self.message}'