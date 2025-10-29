from django.db import models
from products.models import Product
from vendor.models import Vendor
from django.contrib.auth.models import User
from django.utils import timezone
import random, string


def get_invoice_number():
    alpnum = string.ascii_uppercase + string.digits
    end = ''.join(random.choices(alpnum, k=12))
    numbers = ''.join(random.choices(string.digits, k=10))
    return f"INV-{numbers}-{end}"

def generate_order_id():
    prefix = "P-ORDER-"
    last_order = PurchaseOrder.objects.order_by("-id").first()

    if not last_order:
        new_num = 1
    else:
        last_id = last_order.order_id
        try:
            last_number = int(last_id.split("-")[-1])
            new_num = last_number + 1
        except (IndexError, ValueError):
            new_num = last_order.id + 1
    return f"{prefix}{new_num:03d}"


class PurchaseOrder(models.Model):
    order_id = models.CharField(unique=True, max_length=20, default=generate_order_id)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="purchase_orders")
    invoice_number = models.CharField(max_length=50, unique=True, default=get_invoice_number, editable=False)
    purchase_date = models.DateField(default=timezone.now)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True, null=True)
    is_confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_purchase_order")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Purchase #{self.invoice_number} - {self.vendor.vendor_name}"
    


class PurchaseOrderItem(models.Model):
    purchase = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name="purchase_order_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    line_total = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        # Auto-calculate line total each time
        self.line_total = self.quantity * self.product.purchase_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product} - {self.purchase.order_id}"
