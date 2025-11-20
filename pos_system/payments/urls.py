from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('', views.PaymentListView.as_view(), name="payments_list_view"),
    path('add-payment/', views.PaymentFormView.as_view(), name="payment_form_view"),
    path('confirm-payment/', views.PaymentConfirmView.as_view(), name="payment_confirm_view"),
    path("cancel-payment/", views.CancelPaymentView.as_view(), name="cancel_payment"),
    path("payment/receipt/<int:payment_id>/", views.PaymentReceiptView.as_view(), name="payment_receipt"),
]
