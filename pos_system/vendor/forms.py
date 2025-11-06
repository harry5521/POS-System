# vendors/forms.py
from django import forms
from .models import Vendor

class VendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ['vendor_name', 'contact_person', 'phone', 'email', 'address']
        widgets = {
            'vendor_name': forms.TextInput(attrs={
                'class': 'input-field',
                'placeholder': 'Vendor Name',
                'required': True
            }),
            'contact_person': forms.TextInput(attrs={
                'class': 'input-field',
                'placeholder': 'Contact Person Name',
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'class': 'input-field',
                'placeholder': 'Phone Number',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'input-field',
                'placeholder': 'Email Address (optional)',
            }),
            'address': forms.Textarea(attrs={
                'class': 'input-field',
                'placeholder': 'Full Address',
                'rows': 2,
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        vendor_name = cleaned_data.get('vendor_name')
        contact_person = cleaned_data.get('contact_person')
        phone = cleaned_data.get('phone')

        # Required field validation
        if not vendor_name:
            self.add_error('vendor_name', 'Vendor Name is required.')
        if not contact_person:
            self.add_error('contact_person', 'Contact Person is required.')
        if not phone:
            self.add_error('phone', 'Phone Number is required.')

        # Uniqueness validation (Vendor Name)
        if vendor_name:
            qs = Vendor.objects.filter(vendor_name__iexact=vendor_name)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                self.add_error('vendor_name', 'Vendor name already exists.')

        # Uniqueness validation (Phone)
        if phone:
            qs = Vendor.objects.filter(phone=phone)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                self.add_error('phone', 'Phone number already exists.')

        return cleaned_data

    # def clean(self):
    #     cleaned_data = super().clean()
    #     vendor_name = cleaned_data.get('vendor_name')
    #     contact_person = cleaned_data.get('contact_person')
    #     phone = cleaned_data.get('phone')

    #     if not vendor_name:
    #         self.add_error('vendor_name', 'This field is required.')
    #     if not contact_person:
    #         self.add_error('contact_person', 'This field is required.')
    #     if not phone:
    #         self.add_error('phone', 'This field is required.')

    # def clean_name(self):
    #     vendor_name = self.cleaned_data.get('vendor_name')
    #     qs = Vendor.objects.filter(vendor_name=vendor_name)
    #     if self.instance.pk:
    #         qs = qs.exclude(pk=self.instance.pk)
    #     if qs.exists():
    #         raise forms.ValidationError('Vendor name already exists.')
    #     return vendor_name

    # def clean_phone(self):
    #     phone = self.cleaned_data.get('phone')
    #     qs = Vendor.objects.filter(phone=phone)
    #     if self.instance.pk:
    #         qs = qs.exclude(pk=self.instance.pk)
    #     if qs.exists():
    #         raise forms.ValidationError('Phone No already exists.')
    #     return phone