from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db import models
from django.contrib.auth import get_user_model

class CustomUser(AbstractUser):
    # -------- Personal Info --------
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[("Male", "Male"), ("Female", "Female"), ("Other", "Other")], blank=True)
    is_verified = models.BooleanField(default=False)

    is_s_a = models.BooleanField(default=False)
    shipping_first_name = models.CharField(max_length=50, blank=True)
    shipping_last_name = models.CharField(max_length=50, blank=True)
    shipping_address_1 = models.CharField(max_length=255, blank=True)
    shipping_address_2 = models.CharField(max_length=255, blank=True)
    shipping_zip_code = models.CharField(max_length=10, blank=True)
    shipping_state = models.CharField(max_length=50, blank=True)
    shipping_city = models.CharField(max_length=50, blank=True)
    shipping_note = models.TextField(blank=True)
    shipping_number = models.CharField(max_length=15 , blank=True)
    shipping_second_number = models.CharField(max_length=15, blank=True)
    shipping_landmark = models.CharField(max_length=250 , blank=True)
    shipping_house_no = models.CharField(max_length=250 , blank=True)
    user_returns = models.PositiveIntegerField(default=0)
    terms_conditions = models.BooleanField(default=False)
    # -------- Marketing Info --------
    marketing_opt_in = models.BooleanField(default=True)

    STATUS_CHOICES = [
        ('New_customer', 'New Customer'),
        ('CART', 'Added to Cart'),
        ('Havepurchased', 'Have Purchased'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='New_customer')

    product_liked = models.JSONField(default=list, blank=True)
    product_in_cart = models.JSONField(default=list, blank=True)
    product_purchased = models.JSONField(default=list, blank=True)
    product_viewed = models.JSONField(default=list, blank=True)

    pages_viewed = models.JSONField(default=list, blank=True)
    purchase_dates = models.JSONField(default=list, blank=True)      # list of ISO date strings
    purchase_timings = models.JSONField(default=list, blank=True)    # list of time strings or ISO timestamps

    button_clicked = models.JSONField(default=list, blank=True)
    search_by_user = models.JSONField(default=list, blank=True)

    last_visit = models.DateTimeField(null=True, blank=True)
    last_email_sent = models.JSONField(default=list , blank=True)

    #personal
    u_discounts = models.CharField(max_length=250 , blank=True)
    def __str__(self):
        return self.username



User = get_user_model()

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    product = models.CharField(max_length= 250)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
