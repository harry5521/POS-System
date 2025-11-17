from django.db import models
from django.utils import timezone
from customer.models import Customer
from vendor.models import Vendor
from sales.models import SalesOrder
from purchases.models import PurchaseOrder
from django.contrib.auth.models import User
from django.db import transaction
from decimal import Decimal

# Create your models here.

class Payment(models.Model):
    PAYMENT_TYPE_CHOICES = [
        ('customer', 'Customer Payment'),
        ('vendor', 'Vendor Payment'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('bank', 'Bank Transfer'),
        ('other', 'Other'),
    ]

    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash')

    # Relations (nullable because payment could be for either side)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True)
    sales_order = models.ForeignKey(SalesOrder, on_delete=models.SET_NULL, null=True, blank=True, related_name='sales_payments')
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.SET_NULL, null=True, blank=True, related_name='purchase_payments')

    # Payment details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reference_no = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    payment_date = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='payments_created')  

    class Meta:
        ordering = ['-payment_date']
        verbose_name = "Payment"
        verbose_name_plural = "Payments"

    def __str__(self):
        if self.payment_type == 'customer' and self.customer:
            return f"Customer Payment - {self.customer.name} ({self.amount})"
        elif self.payment_type == 'vendor' and self.vendor:
            return f"Vendor Payment - {self.vendor.vendor_name} ({self.amount})"
        return f"Payment #{self.id} - {self.amount}"


    @transaction.atomic
    def apply_payment(self):
        """
        Apply vendor or customer payment to the linked order.
        Ensures no overpayment and updates order status accordingly.
        """

        amount = Decimal(self.amount)

        if amount <= 0:
            raise ValueError("Payment amount must be greater than zero.")

        # ────────────── CUSTOMER PAYMENT ──────────────
        if self.payment_type == "customer":
            if not self.sales_order:
                raise ValueError("Customer payment must be linked with a Sales Order.")
            if not self.customer:
                raise ValueError("Customer payment must be linked with a Customer.")
            order = self.sales_order

            # Already fully paid
            if order.status == "Paid":
                raise ValueError("Sales Order is already fully paid.")

            # ── First-time payment (unpaid order) ──
            if order.remaining_amount == 0 and order.status == "unpaid":
                if amount > order.total_amount:
                    raise ValueError("Payment amount can't exceed the total amount.")

                if amount == order.total_amount:
                    order.remaining_amount = 0
                    order.status = "Paid"
                else:
                    order.remaining_amount = Decimal(order.total_amount) - amount
                    order.status = "Partial"

                order.save(update_fields=["remaining_amount", "status"])

            # ── Subsequent payment (partial order) ──
            else:
                if amount > order.remaining_amount:
                    raise ValueError("Payment amount can't exceed the remaining amount.")

                order.remaining_amount = Decimal(order.remaining_amount) - amount
                if order.remaining_amount == 0:
                    order.status = "Paid"

                order.save(update_fields=["remaining_amount", "status"])


        # ────────────── VENDOR PAYMENT ──────────────
        elif self.payment_type == "vendor":
            if not self.purchase_order:
                raise ValueError("Vendor payment must be linked with a Purchase Order.")
            if not self.vendor:
                raise ValueError("Vendor payment must be linked with a Vendor.")
            order = self.purchase_order

            # Already fully paid
            if order.status == "Paid":
                raise ValueError("Purchase Order is already fully paid.")

            # ── First-time payment (unpaid order) ──
            if order.remaining_amount == 0 and order.status == "unpaid":
                if amount > order.total_amount:
                    raise ValueError("Payment amount can't exceed the total amount.")

                if amount == order.total_amount:
                    order.remaining_amount = 0
                    order.status = "Paid"
                else:
                    order.remaining_amount = Decimal(order.total_amount) - amount
                    order.status = "Partial"

                order.save(update_fields=["remaining_amount", "status"])

            # ── Subsequent payment (partial order) ──
            else:
                if amount > order.remaining_amount:
                    raise ValueError("Payment amount can't exceed the remaining amount.")

                order.remaining_amount = Decimal(order.remaining_amount) - amount
                if order.remaining_amount == 0:
                    order.status = "Paid"

                order.save(update_fields=["remaining_amount", "status"])

        else:
            raise ValueError("Invalid payment type or missing linked order.")
