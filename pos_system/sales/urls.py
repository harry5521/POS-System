from django.urls import path
from . import views

app_name = "sales"

urlpatterns = [
    path('', views.SalesListView.as_view(), name="sales_list_view"),
]
