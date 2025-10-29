from django.urls import path
from . import views

app_name = 'purchases'

urlpatterns = [
    path('', views.PurchaseListView.as_view(), name='purchase_list_view'),
    path('order-detail/<int:pk>/', views.PurchaseOrderDetailView.as_view(), name='p_order_detail_view'),
    path('create-purchase-order/', views.PurchaseOrderFormView.as_view(), name='purchase_order_form_view'),
    path('order-items/<int:pk>/', views.PurchaseOrderItemsFormView.as_view(), name='p_order_items_form_view'),
]

