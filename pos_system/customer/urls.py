from django.urls import path
from . import views

app_name = 'customer'

urlpatterns = [
    path('', views.CustomerListView.as_view(), name='customer_list_view'),
    path('add-customer/', views.CustomerFormView.as_view(), name='customer_form_view'),
    path('update-customer/<int:pk>/', views.CustomerUpdateView.as_view(), name='customer_update_view'),
    # path('delete-customer/<int:pk>/', views.CustomerDeleteView.as_view(), name='customer_delete_view'),
]
