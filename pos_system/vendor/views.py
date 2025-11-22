from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import Vendor
from .forms import VendorForm
from django.db.models import Q


# Create your views here.

class VendorFormView(LoginRequiredMixin, CreateView):
    model = Vendor
    template_name = 'vendor/vendor_form.html'
    form_class = VendorForm
    success_url = reverse_lazy('vendor:vendor_form_view')

    def form_valid(self, form):
        response = super().form_valid(form)
        vendor = self.object.vendor_name
        messages.success(self.request, f"Vendor '{vendor}' created successfully!")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the highlighted errors.")
        return super().form_invalid(form)

class VendorListView(LoginRequiredMixin, ListView):
    model = Vendor
    template_name = 'vendor/vendor_list.html'
    context_object_name = 'vendors'
    paginate_by = 50

    def get_queryset(self):
        query = self.request.GET.get('vendor-search', '')

        vendors = Vendor.objects.all()
        if query:
            vendors = Vendor.objects.filter(
                Q(vendor_name__icontains=query) | Q(email__icontains=query)
            )
        return vendors
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("vendor-search", "")
        return context

class VendorUpdateView(LoginRequiredMixin, UpdateView):
    model = Vendor
    template_name = 'vendor/vendor_form.html'
    form_class = VendorForm
    success_url = reverse_lazy('vendor:vendor_list_view')

    def form_valid(self, form):
        response = super().form_valid(form)
        vendor = self.object.vendor_name
        messages.success(self.request, f"Vendor '{vendor}' updated successfully!")
        return response

class VendorDeleteView(LoginRequiredMixin, DeleteView):
    model = Vendor
    template_name = 'vendor/vendor_list.html'
    success_url = reverse_lazy('vendor:vendor_list_view')