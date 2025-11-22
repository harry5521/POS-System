from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.contrib import messages
from .models import PurchaseOrder, PurchaseOrderItem
from products.models import Product
from .forms import PurchaseOrderForm

# Create your views here.

class PurchaseListView(LoginRequiredMixin, ListView):
    model = PurchaseOrder
    template_name = 'purchases/p_orders_list.html'
    context_object_name = 'p_orders'
    paginate_by = 100

    def get_queryset(self):
        query = self.request.GET.get("p-order-search")
        p_orders = PurchaseOrder.objects.all().order_by("-created_at").prefetch_related("purchase_order_items", "vendor")
        if query:
            p_orders = p_orders.filter(
                Q(status__contains=query) |
                Q(order_id__icontains=query) |
                Q(vendor__vendor_name__icontains=query) |
                Q(invoice_number__icontains=query)
            )
        return p_orders
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("p-order-search", "")
        return context


class PurchaseOrderFormView(LoginRequiredMixin, CreateView):
    model = PurchaseOrder
    template_name = 'purchases/p_order_form.html'
    form_class = PurchaseOrderForm
    success_url = reverse_lazy("purchases:purchase_list_view")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        order_id = self.object.order_id
        messages.success(self.request, f"Purchase Order with {order_id} has been created.")
        return response

class PurchaseOrderDetailView(LoginRequiredMixin, DetailView):
    model = PurchaseOrder
    template_name = 'purchases/p_order_detail.html'
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["items"] = self.object.purchase_order_items.select_related("product")
        return context

class PurchaseOrderItemsFormView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        order_id = kwargs.get('pk')
        order = get_object_or_404(PurchaseOrder, pk=order_id)
        products = Product.objects.all()
        print(order_id, order.order_id)
        return render(request, "purchases/p_order_items_form.html", {'order':order, 'products':products})
    
    def post(self, request, *args, **kwargs):
        order_id = kwargs.get('pk')
        order = get_object_or_404(PurchaseOrder, pk=order_id)
        product = request.POST.getlist("product[]")
        quantity = request.POST.getlist("quantity[]")

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
        print(order_id)

        bulk_items = []
        for p_id, qty in valid_items.items():
            # print(p_id, qty)
            product = Product.objects.get(pk=p_id)
            # print(product.product_name)
            existing_item = PurchaseOrderItem.objects.filter(purchase=order, product=product).first()
            if existing_item:
                existing_item.quantity += qty
                added_amount = product.purchase_price * qty
                existing_item.line_total += added_amount
                existing_item.save(update_fields=['quantity', 'line_total'])
                order.total_amount += added_amount
            else:    
                bulk_items.append(
                    PurchaseOrderItem(
                        purchase=order,
                        product=product,
                        quantity=qty,
                        purchase_price=product.purchase_price,
                        line_total=product.purchase_price * qty
                    )
                )
        # print(bulk_items)

        if bulk_items:
            PurchaseOrderItem.objects.bulk_create(bulk_items)

        total = sum(item.line_total for item in bulk_items)
        order.total_amount += total
        order.save(update_fields=['total_amount'])

        messages.success(request, f"Items Added for Purchase Order {order.order_id}")
        return redirect("purchases:purchase_list_view")
    

class DeletePurchaseOrderItemsView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        order_id = kwargs.get('pk')
        order = get_object_or_404(PurchaseOrder, pk=order_id)
        # print(order_id, order.order_id)
        items = order.purchase_order_items.select_related("product")
        # print(items)
        return render(request, "purchases/p_order_delete_items.html", {'order':order, 'items':items})
    
    def post(self, request, *args, **kwargs):
        order_id = kwargs.get('pk')
        order = get_object_or_404(PurchaseOrder, pk=order_id)

        checked_items = request.POST.getlist("delete_items[]")
        # print(checked_items)

        for item_id in checked_items:
            item = get_object_or_404(PurchaseOrderItem, pk=item_id, purchase=order)
            order.total_amount -= item.line_total
            item.delete()

        order.total_amount = max(order.total_amount, 0)
        order.save()
        messages.success(request, "Selected items have been deleted.")
        return redirect("purchases:purchase_list_view")