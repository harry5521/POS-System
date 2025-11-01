from django import forms
from .models import Product
from vendor.models import Vendor

class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = ['product_name', 'barcode', 'purchase_price', 'sale_price',
                   'quantity', 'low_stock', 'vendor', 'category']
        
        widgets = {
            'product_name': forms.TextInput(attrs={
                'placeholder': 'Product Name',
                'class': 'input-field',
                'required': True
            }),
            'barcode': forms.TextInput(attrs={
                'placeholder': 'Barcode',
                'class': 'input-field',
                'autofocus': True,
                'required': True
            }),
            'purchase_price': forms.NumberInput(attrs={
                'placeholder': 'Purchase Price',
                'step': '0.01',
                'class': 'input-field',
                'required': True
            }),
            'sale_price': forms.NumberInput(attrs={
                'placeholder': 'Sale Price',
                'step': '0.01',
                'class': 'input-field',
                'required': True
            }),
            'quantity': forms.NumberInput(attrs={
                'placeholder': 'Quantity',
                'class': 'input-field',
                'required': True
            }),
            'low_stock': forms.NumberInput(attrs={
                'placeholder': 'Low Stock Limit',
                'class': 'input-field',
                'required': True
            }),
            'category': forms.Select(attrs={
                'class': 'input-field',
                'required': False
            }, choices=[
                ('', 'Select Category'),
                ('grocery', 'Grocery'),
                ('electronics', 'Electronics'),
                ('furniture', 'Furniture')
            ]),
            'vendor': forms.Select(attrs={
                'class': 'input-field',
                'required': True
            },)
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vendor'].queryset = Vendor.objects.all()
        self.fields['vendor'].empty_label = "Select Vendor"

    def clean(self):
        cleaned_data = super().clean()
        barcode = cleaned_data.get("barcode")
        vendor = cleaned_data.get("vendor")
        purchase_price = cleaned_data.get("purchase_price")
        sale_price = cleaned_data.get("sale_price")
        quantity = cleaned_data.get("quantity")
        low_stock = cleaned_data.get("low_stock")

        if not vendor:
            self.add_error('vendor', 'Please select a vendor.')

        # --- Barcode uniqueness (skip when updating same product) ---
        if not barcode:
            self.add_error('barcode', 'Barcode is required.')
        if barcode:
            qs = Product.objects.filter(barcode=barcode)
            # Exclude current instance (so same barcode is allowed when updating itself)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                self.add_error('barcode', 'This Barcode already exists.')


        # --- Purchase & Sale Price Validation ---
        if not purchase_price:
            self.add_error('purchase_price', 'Purchase price is required.')
        if not sale_price:
            self.add_error('sale_price', 'Sale price is required.')
        if purchase_price is not None and sale_price is not None:
            if purchase_price >= sale_price:
                self.add_error('sale_price', 'Sale price must be greater than purchase price.')

        # --- Stock Validation ---
        if not quantity:
            self.add_error('quantity', 'Quantity is required.')
        if not low_stock:
            self.add_error('low_stock', 'Low stock limit is required.')
        if quantity is not None and low_stock is not None:
            if low_stock > quantity:
                self.add_error('low_stock', 'Low stock must be less than or equal to quantity.')

        return cleaned_data



