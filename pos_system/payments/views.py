from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import FormView, CreateView
from django.contrib import messages
from django.views import View
from .models import Payment
from customer.models import Customer
from vendor.models import Vendor
from sales.models import SalesOrder
from purchases.models import PurchaseOrder
from .forms import PaymentForm
from django.db.models import Q
from django.db import transaction

# Create your views here.

def clear_pending_payment(request):
    """Remove any pending payment data from session (safe delete)."""
    if request.session.get("pending_payment") is not None:
        try:
            del request.session["pending_payment"]
        except KeyError:
            pass


class PaymentListView(ListView):
    model = Payment
    template_name = 'payments/payments_list.html'
    context_object_name = 'payments'

    def get_queryset(self):
        query = self.request.GET.get('payment-search', '')
        payments = Payment.objects.all()

        if query:
            payments = payments.filter(
                Q(customer__name__icontains=query) |
                Q(vendor__vendor_name__icontains=query) |
                Q(reference_no__icontains=query)
            )
        return payments
    

class PaymentFormView(View):
    template_name = "payments/payment_form.html"

    def get(self, request):
        clear_pending_payment(request)
        form = PaymentForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = PaymentForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data.copy()

            # Store only IDs or primitive data in session (not model instances)
            session_data = {
                "payment_type": data.get("payment_type"),
                "payment_method": data.get("payment_method"),
                "customer_id": data["customer"].id if data.get("customer") else None,
                "vendor_id": data["vendor"].id if data.get("vendor") else None,
                "sales_order_id": data["sales_order"].id if data.get("sales_order") else None,
                "purchase_order_id": data["purchase_order"].id if data.get("purchase_order") else None,
                "amount": float(data.get("amount", 0)),
                "reference_no": data.get("reference_no"),
                "notes": data.get("notes"),
            }

            request.session["pending_payment"] = session_data
            print(request.session["pending_payment"])
            return redirect("payments:payment_confirm_view")

        messages.error(request, "Please correct the highlighted errors.")
        return render(request, self.template_name, {"form": form})


class CancelPaymentView(View):
    def get(self, request):
        print(request.session["pending_payment"])
        clear_pending_payment(request)
        print("Payment cancelled. Session cleared.")
        print(request.session.get("pending_payment"))
        messages.info(request, "Payment process cancelled.")
        return redirect("payments:payments_list_view")

class PaymentConfirmView(View):
    template_name = "payments/payment_confirm.html"

    def get(self, request):
        data = request.session.get("pending_payment")
        if not data:
            messages.error(request, "No payment data found. Please record payment again.")
            return redirect("payments:add_payment")

        context = {"data": data}

        # Fetch related objects for display
        if data["payment_type"] == "customer":
            context["customer"] = Customer.objects.filter(id=data["customer_id"]).first()
            context["sales_order"] = SalesOrder.objects.filter(id=data["sales_order_id"]).first()
        elif data["payment_type"] == "vendor":
            context["vendor"] = Vendor.objects.filter(id=data["vendor_id"]).first()
            context["purchase_order"] = PurchaseOrder.objects.filter(id=data["purchase_order_id"]).first()
            

        print(context)
        return render(request, self.template_name, context)

    def post(self, request):
        """When user confirms the payment"""
        data = request.session.get("pending_payment")
        if not data:
            messages.error(request, "Session expired. Please record payment again.")
            return redirect("payments:payments_form_view")

        try:
            with transaction.atomic():
                # Create payment record (not committed yet)
                payment = Payment.objects.create(
                    payment_type=data.get("payment_type"),
                    payment_method=data.get("payment_method"),
                    customer_id=data.get("customer_id"),
                    vendor_id=data.get("vendor_id"),
                    sales_order_id=data.get("sales_order_id"),
                    purchase_order_id=data.get("purchase_order_id"),
                    amount=data.get("amount"),
                    reference_no=data.get("reference_no"),
                    notes=data.get("notes"),
                    created_by=request.user,
                )

                # Apply balance logic safely
                payment.apply_payment()

            # If everything successful, clear session
            if "pending_payment" in request.session:
                del request.session["pending_payment"]

            messages.success(request, f"✅ Payment of {payment.amount} recorded successfully!")
            return redirect("payments:payments_list_view")

        except ValueError as e:
            # Logical/validation error from apply_payment
            messages.error(request, f"⚠️ {str(e)}")
            return redirect("payments:payment_confirm_view")

        except Exception as e:
            # Any unexpected issue
            messages.error(request, f"❌ An unexpected error occurred: {str(e)}")
            return redirect("payments:payment_confirm_view")