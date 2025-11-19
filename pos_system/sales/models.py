from django.db import models
from django.utils import timezone
from products.models import Product
from customer.models import Customer
from django.contrib.auth.models import User
import string, random
from decimal import Decimal

# Create your models here.

def generate_invoice_number():
    while True:
        alpnum = string.ascii_uppercase + string.digits
        end = ''.join(random.choices(alpnum, k=6))
        numbers = ''.join(random.choices(string.digits, k=6))
        invoice = f"INV-{numbers}-{end}"
        if not SalesOrder.objects.filter(invoice_number=invoice).exists():
            return invoice

def generate_order_id():
    prefix = "S-ORDER-"
    last_order = SalesOrder.objects.order_by("-id").first()

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

class SalesOrder(models.Model):
    STATUS_CHOICES = [
        ("unpaid", "Unpaid"),
        ("partial", "Partial"),
        ("paid", "Paid"),
    ]

    order_id = models.CharField(max_length=20, unique=True, default=generate_order_id)
    invoice_number = models.CharField(max_length=50, unique=True, default=generate_invoice_number)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    sale_date = models.DateTimeField(default=timezone.now)

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="unpaid")
    payment_method = models.CharField(max_length=20, default="Cash")  # Cash / Card / Credit
    notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_sales_order")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-sale_date']
        verbose_name = "Sales Order"
        verbose_name_plural = "Sales Orders"

    def __str__(self):
        return f"{self.order_id} - #{self.invoice_number}"

    @property
    def due_amount(self):
        """Return how much the customer still owes."""
        return max(self.total_amount - self.paid_amount, 0)
    
    def update_customer_balance(self):
        """Adjust customer's current balance after sale."""
        if self.customer:
            self.customer.current_balance += Decimal(self.total_amount)
            self.customer.save(update_fields=['current_balance'])




class SalesOrderItem(models.Model):
    sales_order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name="sales_items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    line_total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.product_name} ({self.quantity})"

    def save(self, *args, **kwargs):
        # Auto-update line total before save
        self.line_total = self.sale_price * self.quantity
        super().save(*args, **kwargs)
