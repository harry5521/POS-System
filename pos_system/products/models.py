from django.db import models

# Create your models here.

class Product(models.Model):
    product_name = models.CharField(max_length=100)
    barcode = models.CharField(max_length=100, unique=True)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    low_stock = models.PositiveIntegerField()
    category = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.product_name} - {self.barcode}"