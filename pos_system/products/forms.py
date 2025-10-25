from django import forms
from .models import Product

class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = ['product_name', 'barcode', 'purchase_price', 'sale_price',
                   'quantity', 'low_stock', 'category']
        
        widgets = {
            'product_name': forms.TextInput(attrs={
                'placeholder': 'Product Name',
                'class': 'input-field',
                'required': True
            }),
            'barcode': forms.TextInput(attrs={
                'placeholder': 'Barcode',
                'class': 'input-field',
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
        }


    def clean(self):
        cleaned_data = super().clean()
        barcode = cleaned_data.get("barcode")
        purchase_price = cleaned_data.get("purchase_price")
        sale_price = cleaned_data.get("sale_price")
        quantity = cleaned_data.get("quantity")
        low_stock = cleaned_data.get("low_stock")

        # --- Barcode uniqueness (skip when updating same product) ---
        if barcode:
            qs = Product.objects.filter(barcode=barcode)
            # Exclude current instance (so same barcode is allowed when updating itself)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                self.add_error('barcode', 'This Barcode already exists.')


        # --- Purchase & Sale Price Validation ---
        if purchase_price is not None and sale_price is not None:
            if purchase_price >= sale_price:
                self.add_error('sale_price', 'Sale price must be greater than purchase price.')

        # --- Stock Validation ---
        if quantity is not None and low_stock is not None:
            if low_stock > quantity:
                self.add_error('low_stock', 'Low stock must be less than or equal to quantity.')

        return cleaned_data


# class ProductForm(forms.Form):
#     product_name = forms.CharField(max_length=100)
#     barcode = forms.CharField(max_length=100)
#     purchase_price = forms.DecimalField(max_digits=10, decimal_places=2)
#     sale_price = forms.DecimalField(max_digits=10, decimal_places=2)
#     quantity = forms.IntegerField(min_value=0)
#     low_stock = forms.IntegerField(min_value=0)
#     category = forms.CharField(max_length=50, required=False)

#     def __init__(self, *args, instance=None, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.instance = instance

#     def clean(self):
#         cleaned_data = super().clean()
#         barcode = cleaned_data.get("barcode")
#         purchase_price = cleaned_data.get("purchase_price")
#         sale_price = cleaned_data.get("sale_price")
#         quantity = cleaned_data.get("quantity")
#         low_stock = cleaned_data.get("low_stock")

#         if not self.instance:
#             if Product.objects.filter(barcode=barcode).exists():
#                 self.add_error('barcode', 'This Barcode already exists.')

#         if purchase_price >= sale_price:
#             self.add_error('sale_price', 'Sale price must be greater than purchase price.')

#         if low_stock > quantity:
#             self.add_error('low_stock', 'Low stock must be less than or equal to quantity.')

#         return cleaned_data