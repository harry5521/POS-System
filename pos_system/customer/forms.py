from django import forms
from .models import Customer

class CustomerForm(forms.ModelForm):

    class Meta:
        model = Customer
        fields = ['name', 'phone', 'email', 'address']
        read_only_fields = ['current_balance']

        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Customer Name',
                'class': 'input-field',
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': 'Phone Number',
                'class': 'input-field',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Email Address',
                'class': 'input-field',
                'required': False
            }),
            'address': forms.TextInput(attrs={
                'placeholder': 'Address',
                'class': 'input-field',
                'required': False
            })
        }

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get("name")
        phone = cleaned_data.get("phone")

        if not name:
            self.add_error("name", "Name is required.")
        if not phone:
            self.add_error("phone", "Phone number is required.")

        return cleaned_data

