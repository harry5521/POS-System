from django.db import models
from vendor.models import Vendor

# Create your models here.

class Product(models.Model):
    product_name = models.CharField(max_length=100)
    barcode = models.CharField(max_length=100, unique=True)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    low_stock = models.PositiveIntegerField()
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, null=True, blank=True, related_name="products")
    category = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.product_name} - {self.barcode}"