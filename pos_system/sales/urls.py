from django.urls import path
from . import views

# sales/urls.py
app_name = 'sales'

urlpatterns = [
    path('', views.SalesListView.as_view(), name="sales_list_view"),
    path('create-sale-order/', views.SalesOrderFormView.as_view(), name='create_sales_order'),
    path('sales-items/<int:pk>/', views.SalesOrderItemsFormView.as_view(), name='create_sales_order_items'),
    path('sales-order-detail/<int:pk>/', views.SalesOrderDetailView.as_view(), name="sales_detail_view"),

    # API Endpoints
    path("api/product-by-barcode/", views.product_by_barcode, name="product_by_barcode"),

]
