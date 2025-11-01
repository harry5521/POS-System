from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.edit import FormView, CreateView, DeleteView, UpdateView
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import Customer
from .forms import CustomerForm
from django.db.models import Q

# Create your views here.

class CustomerFormView(LoginRequiredMixin, CreateView):
    model = Customer
    template_name = 'customer/customer_form.html'
    form_class = CustomerForm
    success_url = reverse_lazy('customer:customer_list_view')

    def form_valid(self, form):
        messages.success(self.request, "Customer created successfully!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the highlighted errors.")
        return super().form_invalid(form)
    
class CustomerListView(LoginRequiredMixin, ListView):
    model = Customer
    template_name = 'customer/customers_list.html'
    context_object_name = 'customers'

    def get_queryset(self):
        query = self.request.GET.get('customer-search', '')
        customers = Customer.objects.all()
        if query:
            customers = customers.filter(
                Q(name__icontains=query) | Q(phone__icontains=query)
            )
        return customers
    

class CustomerUpdateView(LoginRequiredMixin, UpdateView):
    model = Customer
    template_name = 'customer/customer_form.html'
    form_class = CustomerForm
    success_url = reverse_lazy('customer:customer_list_view')


class CustomerDeleteView(LoginRequiredMixin, DeleteView):
    model = Customer
    template_name = 'customer/customers_list.html'
    success_url = reverse_lazy('customer:customer_list_view')