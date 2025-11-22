from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
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


class PaymentListView(LoginRequiredMixin, ListView):
    model = Payment
    template_name = 'payments/payments_list.html'
    context_object_name = 'payments'
    paginate_by = 150

    def get_queryset(self):
        query = self.request.GET.get('payment-search', '')
        payments = Payment.objects.all()

        if query:
            payments = payments.filter(
                Q(customer__name__icontains=query) |
                Q(vendor__vendor_name__icontains=query) |
                Q(reference_no__icontains=query) |
                Q(created_by__username__icontains=query)
            )
        return payments
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("payment-search", "")
        return context

class PaymentFormView(LoginRequiredMixin, View):
    template_name = "payments/payment_form.html"

    def get(self, request):
        clear_pending_payment(request)
        form = PaymentForm()

        sale_order = request.GET.get("sale_order")
        customer = request.GET.get("customer")

        print(customer)

        initial = {}

        if sale_order and customer:
            initial["payment_type"] = "customer"
            initial["customer"] = customer
            initial["sales_order"] = sale_order

        form = PaymentForm(initial=initial)
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
            # print(request.session["pending_payment"])
            return redirect("payments:payment_confirm_view")

        messages.error(request, "Please correct the highlighted errors.")
        return render(request, self.template_name, {"form": form})


class CancelPaymentView(LoginRequiredMixin, View):
    def get(self, request):
        print(request.session["pending_payment"])
        clear_pending_payment(request)
        print("Payment cancelled. Session cleared.")
        print(request.session.get("pending_payment"))
        messages.info(request, "Payment process cancelled.")
        return redirect("payments:payments_list_view")

class PaymentConfirmView(LoginRequiredMixin, View):
    template_name = "payments/payment_confirm.html"

    def get(self, request):
        data = request.session.get("pending_payment")
        if not data:
            messages.error(request, "No payment data found.")
            return redirect("payments:payment_form_view")

        context = {"data": data}

        if data["payment_type"] == "customer":
            customer = Customer.objects.filter(id=data["customer_id"]).first()
            sales_order = SalesOrder.objects.filter(id=data["sales_order_id"]).first()

            context["party"] = customer            # customer/vendor unified
            context["order"] = sales_order         # unified order object

        elif data["payment_type"] == "vendor":
            vendor = Vendor.objects.filter(id=data["vendor_id"]).first()
            purchase_order = PurchaseOrder.objects.filter(id=data["purchase_order_id"]).first()

            context["party"] = vendor              # customer/vendor unified
            context["order"] = purchase_order      # unified order object

        return render(request, self.template_name, context)


    def post(self, request):
        """When user confirms the payment"""
        data = request.session.get("pending_payment")
        if not data:
            messages.error(request, "Session expired. Please record payment again.")
            return redirect("payments:payment_form_view")

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
            return redirect("payments:payment_receipt", payment_id=payment.id)


        except ValueError as e:
            # Logical/validation error from apply_payment
            messages.error(request, f"⚠️ {str(e)}")
            return redirect("payments:payment_confirm_view")

        except Exception as e:
            # Any unexpected issue
            messages.error(request, f"❌ An unexpected error occurred: {str(e)}")
            return redirect("payments:payment_confirm_view")


class PaymentReceiptView(DetailView):
    model = Payment
    template_name = "payments/payment_recipt.html"
    context_object_name = "payment"
    pk_url_kwarg = "payment_id"   # URL will contain <payment_id>

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add extra useful info for the receipt
        context["request"] = self.request

        return context
