from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.contrib import messages
from .models import SalesOrder, SalesOrderItem
from products.models import Product

# Create your views here.

class SalesListView(ListView):
    model = SalesOrder
    template_name = 'sales/sales_list.html'
    context_object_name = 'sales_orders'

    def get_queryset(self):
        query = self.request.GET.get("sale-search", "")
        sales = SalesOrder.objects.all().order_by('-created_at').prefetch_related('sales_items')

        if query:
            sales = sales.filter(
                Q(order_id__icontains=query) |
                Q(invoice_number__icontains=query) |
                Q(customer__name__icontains=query) |
                Q(status__icontains=query)
            )
        return sales