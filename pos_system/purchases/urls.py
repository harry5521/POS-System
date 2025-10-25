from django.urls import path
from . import views

app_name = 'purchases'

urlpatterns = [
    path('', views.PurchaseListView.as_view(), name='purchase_list_view'),
    path('create-purchase-order/', views.PurchaseOrderForm.as_view(), name='purchase_order_form_view'),
]

