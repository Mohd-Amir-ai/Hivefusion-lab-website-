from django.db import models
from django.conf import settings
from decimal import Decimal
from django.contrib.auth import get_user_model

User = get_user_model()

class Order(models.Model):
    PAYMENT_STATUS = [('pending','pending'), ('paid','paid'), ('cancelled','cancelled')]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Inputs / policy
    shipping_charge = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('50.00'))
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    discount_type = models.CharField(max_length=10, choices=[('flat','flat'),('percent','percent')], default='flat')

    # Computed breakdown (store all to make order immutable)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)        # sum(price*qty)
    taxable_value = models.DecimalField(max_digits=12, decimal_places=2)  # (subtotal - discount) + (shipping if taxable)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2)        # e.g., 18.00
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2)     # total tax
    cgst_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    sgst_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    igst_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    shipping_taxable = models.BooleanField(default=True)
    total = models.DecimalField(max_digits=14, decimal_places=2)

    # Extras
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    notes = models.TextField(blank=True, null=True)

    # Keep original raw snapshot as JSON to ensure rebuildability
    raw_snapshot = models.JSONField(default=dict)  # items, client-provided prices, coupon code, etc.

    def __str__(self):
        return f"Order #{self.pk} - {self.total} - {self.created_at:%Y-%m-%d}"
