from django.urls import path
from . import views

app_name = 'vendor'

urlpatterns = [
    path('', views.VendorListView.as_view(), name="vendor_list_view"),
    path('add-vendor/', views.VendorFormView.as_view(), name="vendor_form_view"),
    path('update-vendor/<int:pk>/', views.VendorUpdateView.as_view(), name="vendor_update_view"),
    # path('delete-vendor/<int:pk>/', views.VendorDeleteView.as_view(), name="vendor_delete_view"),
]
