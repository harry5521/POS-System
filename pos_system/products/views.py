from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import Product, Category
from .forms import ProductForm
from django.db.models import Q

# Create your views here.

class CategoryCreateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        cat_name = request.POST.get("cat_name")

        if not cat_name or cat_name.strip() == "":
            messages.error(request, "Category Name is Required")
            return redirect("products:products_list_view")

        Category.objects.create(cat_name=cat_name.strip())

        messages.success(request, "Category added successfully!")
        return redirect("products:products_list_view")


class ProductFormView(LoginRequiredMixin, CreateView):
    model = Product
    template_name = 'products/product_form.html'
    form_class = ProductForm
    success_url = reverse_lazy('products:product_form_view')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        product = self.object.product_name
        messages.success(self.request, f"Product '{product}' created successfully!")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the highlighted errors.")
        return super().form_invalid(form)
    
class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'products/products_list.html'
    context_object_name = 'products'
    paginate_by = 50

    def get_queryset(self):
        query = self.request.GET.get('product-search', '')

        products = Product.objects.all().select_related('category')
        if query:
            products = products.filter(
                Q(product_name__icontains=query) | 
                Q(barcode__icontains=query) |
                Q(vendor__vendor_name__icontains=query)

            )
        return products
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("product-search", "")
        return context
    

class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    template_name = 'products/product_form.html'
    form_class = ProductForm
    success_url = reverse_lazy('products:products_list_view')

    def form_valid(self, form):
        response = super().form_valid(form)
        product = self.object.product_name
        messages.success(self.request, f"Product '{product}' updated successfully!")
        return response


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'products/products_list.html'
    success_url = reverse_lazy('products:products_list_view')