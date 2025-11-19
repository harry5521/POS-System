from django.urls import path
from . import views


app_name = 'products'

urlpatterns = [
    path('add-product/', views.ProductFormView.as_view(), name='product_form_view'),
    path('add-category/', views.CategoryCreateView.as_view(), name='category_create_view'),
    path('', views.ProductListView.as_view(), name='products_list_view'),
    path('update-product/<int:pk>/', views.ProductUpdateView.as_view(), name='product_update_view'),
    # path('delete-product/<int:pk>/', views.ProductDeleteView.as_view(), name='product_delete_view'),
]
