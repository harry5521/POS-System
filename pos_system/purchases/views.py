from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.contrib import messages
from .models import PurchaseOrder
from .forms import PurchaseOrderForm

# Create your views here.

class PurchaseListView(LoginRequiredMixin, ListView):
    model = PurchaseOrder
    template_name = 'purchases/p_orders_list.html'
    context_object_name = 'p_orders'

    def get_queryset(self):
        query = self.request.GET.get("p-order-search")
        p_orders = PurchaseOrder.objects.all().order_by("-created_at").prefetch_related("purchase_order_items", "vendor")
        if query:
            p_orders = p_orders.filter(
                Q(order_id__icontains=query) |
                Q(vendor__vendor_name__icontains=query) |
                Q(invoice_number__icontains=query) 
            )
        return p_orders

    
class PurchaseOrderForm(CreateView):
    model = PurchaseOrder
    template_name = 'purchases/p_order_form.html'
    form_class = PurchaseOrderForm
    success_url = reverse_lazy("purchases:p_orders_list.html")

    def form_valid(self, form):
        response = super().form_valid(form)
        order_id = self.object.order_id
        messages.success(self.request, f"Purchase Order with {order_id} has been created.")
        return response
    
    
    