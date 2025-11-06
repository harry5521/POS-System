from django import forms
from .models import Payment
from purchases.models import PurchaseOrder

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = [
            'payment_type', 'payment_method',
            'customer', 'sales_order',
            'vendor', 'purchase_order',
            'amount', 'reference_no', 'notes'
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Optional dynamic cleanup
        for field in ['customer', 'vendor', 'sales_order', 'purchase_order']:
            self.fields[field].required = False

        self.fields['purchase_order'].queryset = PurchaseOrder.objects.all().order_by('-created_at')
