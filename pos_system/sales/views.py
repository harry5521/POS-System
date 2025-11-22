from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.contrib import messages
from .models import SalesOrder, SalesOrderItem
from .forms import SalesOrderForm
from products.models import Product

# Create your views here.

class SalesListView(LoginRequiredMixin, ListView):
    model = SalesOrder
    template_name = 'sales/sales_list.html'
    context_object_name = 'sales_orders'
    paginate_by = 150

    def get_queryset(self):
        query = self.request.GET.get("sale-search", "")
        sales = SalesOrder.objects.all().order_by('-created_at').prefetch_related('sales_items')

        if query:
            sales = sales.filter(
                Q(status__contains=query) |
                Q(order_id__icontains=query) |
                Q(invoice_number__icontains=query) |
                Q(customer__name__icontains=query)
            )
        return sales

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("sale-search", "")
        return context
        


class SalesOrderFormView(LoginRequiredMixin, CreateView):
    model = SalesOrder
    template_name = 'sales/sales_form.html'
    form_class = SalesOrderForm

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        order_id = self.object.order_id
        messages.success(self.request, f"Sales Order with {order_id} has been created.")
        return response
    
    def get_success_url(self):
        return reverse_lazy("sales:create_sales_order_items", kwargs={'pk': self.object.pk})

class SalesOrderItemsFormView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        order_id = kwargs.get('pk')
        order = get_object_or_404(SalesOrder, pk=order_id)
        products = Product.objects.all()
        return render(request, "sales/sales_items_form.html", {'order':order, 'products':products})
    
    def post(self, request, *args, **kwargs):
        order_id = kwargs.get('pk')
        order = get_object_or_404(SalesOrder, pk=order_id)
        product = request.POST.getlist("product[]")
        quantity = request.POST.getlist("quantity[]")
        discount = request.POST.get("discount")
        final_total = request.POST.get("final_total")

        # print(order_id)
        # print(order.order_id)
        # print(product)
        # print(quantity)
        # print(gand_total)
        # print(discount)
        # print(final_total)

        valid_items = {}
        for p, qty in zip(product, quantity):
            if not p or not qty:
                continue
            q = int(qty)
            if p in valid_items:
                valid_items[p] += q
            else:
                valid_items[p] = q
        print(valid_items)


        bulk_items = []
        for p_id, qty in valid_items.items():
            print(p_id, qty)
            product = Product.objects.get(pk=p_id)
            
            bulk_items.append(
                SalesOrderItem(
                    sales_order=order,
                    product=product,
                    quantity=qty,
                    sale_price=product.sale_price,
                    line_total=product.sale_price * qty
                    )
            )

        for pr, qty in valid_items.items():
            if not pr or not qty:
                continue
            product = Product.objects.get(pk=pr)
            product.quantity -= qty
            product.save(update_fields=['quantity'])

        if bulk_items:
            SalesOrderItem.objects.bulk_create(bulk_items)

        total = sum(item.line_total for item in bulk_items)
        order.subtotal += total
        order.discount = discount
        order.total_amount = final_total
        order.save(update_fields=['subtotal', 'discount', 'total_amount'])
        order.update_customer_balance()
        messages.success(request, f"Items Added for Sales Order {order.order_id}")

        url = reverse("payments:payment_form_view")
        query = f"?sale_order={order_id}&customer={order.customer.id}"
        return redirect(url + query)



class SalesOrderDetailView(LoginRequiredMixin, DetailView):
    model = SalesOrder
    template_name = 'sales/sales_details.html'
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["items"] = self.object.sales_items.select_related("product")
        return context


# AJAX view to get product details by barcode
def product_by_barcode(request):
    
    barcode = request.GET.get("barcode", "")
    print(barcode)

    try:
        product = Product.objects.get(barcode=barcode)
        return JsonResponse({
            "id": product.id,
            "name": product.product_name,
            "sale_price": str(product.sale_price),
            "stock": product.quantity,
        })
    except Product.DoesNotExist:
        return JsonResponse({"error": "Product not found"}, status=404)
