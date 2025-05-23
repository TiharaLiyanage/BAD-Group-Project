from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import EmailValidator
from django.utils import timezone
from datetime import timedelta

class Category(models.Model):
    name = models.CharField(max_length=100)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order']

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    CATEGORY_CHOICES = [
        ('MAIN', 'Main Dishes'),
        ('RICE', 'Rice & Curry'),
        ('SAND', 'Sandwiches'),
        ('SIDE', 'Sides'),
    ]

    MEAT_CHOICES = [
        ('VEG', 'Vegetarian'),
        ('CHK', 'Chicken'),
        ('BEF', 'Beef'),
        ('PRK', 'Pork'),
        ('FIS', 'Fish'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    category = models.CharField(max_length=4, choices=CATEGORY_CHOICES)
    meat_category = models.CharField(
        max_length=3,
        choices=MEAT_CHOICES,
        default='VEG'
    )
    image = models.CharField(max_length=100)
    is_special = models.BooleanField(default=False)
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_items', blank=True)

    def has_user_liked(self, user):
        """Check if a specific user has liked this item"""
        return self.likes.filter(id=user.id).exists()

    @property
    def like_count(self):
        return self.likes.count()

    def __str__(self):
        return f"{self.name} - {self.get_category_display()}"


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())

    def __str__(self):
        return f"Cart #{self.id} - {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total_price(self):
        return self.menu_item.price * self.quantity

    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name}"


class Order(models.Model):
    ORDER_STATUS = (
        ('preparing', 'In Progress'),
        ('ready', 'Ready'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='preparing')
    total = models.DecimalField(max_digits=8, decimal_places=2)
    delivery_address = models.TextField()
    contact_number = models.CharField(max_length=15)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"

    class Meta:
        ordering = ['-created_at']

    @property
    def can_cancel(self):
        return (self.status in ['preparing', 'ready'] and
                timezone.now() <= self.created_at + timedelta(minutes=5))

    @property
    def cancel_deadline(self):
        return self.created_at + timedelta(minutes=5)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=6, decimal_places=2)

    @property
    def total_price(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.TextField(blank=True)
    mobile_number = models.CharField(max_length=20, blank=True)
    currency = models.CharField(max_length=3, default='LKR')

    def __str__(self):
        return f"{self.user.username}'s Profile"

# Create profile when user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

# Save profile when user is saved
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(validators=[EmailValidator()])
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.name} ({self.email})"