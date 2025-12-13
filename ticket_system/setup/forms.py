from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import Area, Customer, ItemCategory, Item, Machine, Operator

class AreaForm(forms.ModelForm):
    class Meta:
        model = Area
        fields = ['name', 'description', 'status']

    def clean_status(self):
        status = self.cleaned_data.get('status')
        if status == Area.Status.INACTIVE and self.instance.pk:
            # Re-run model validation to catch dependencies
            try:
                self.instance.status = status
                self.instance.clean()
            except ValidationError as e:
                raise forms.ValidationError(e.message)
        return status


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'contact_info', 'customer_type', 'area', 'status']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter active areas only
        self.fields['area'].queryset = Area.objects.filter(status=Area.Status.ACTIVE)

    def clean_status(self):
        status = self.cleaned_data.get('status')
        # Check logic for preventing deactivation is in model.clean()
        # but we can also enforce it here for user feedback
        if status != Customer.Status.ACTIVE and self.instance.pk:
             try:
                self.instance.status = status
                self.instance.clean()
             except ValidationError as e:
                raise forms.ValidationError(e.message)
        return status


class ItemCategoryForm(forms.ModelForm):
    class Meta:
        model = ItemCategory
        fields = ['name', 'description']


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'category', 'gsm', 'width', 'thickness', 'specifications', 'unit_price']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If item is used in approved sales orders, make price readonly
        # This requires checking the reverse relation, assuming 'sales_order_lines'
        if self.instance.pk:
             # We need to import SalesOrder or check relation. 
             # To avoid circular dependency, we might check:
             # if self.instance.salesorderline_set.filter(sales_order__status='Approved').exists():
             #    self.fields['unit_price'].disabled = True
             pass 


class MachineForm(forms.ModelForm):
    class Meta:
        model = Machine
        fields = ['name', 'area', 'speed_capacity', 'max_width_capacity', 'maintenance_notes', 'status']

    def clean_status(self):
        status = self.cleaned_data.get('status')
        if status == Machine.Status.DISABLED and self.instance.pk:
            # Check for active jobs (logic placeholder as requested in plan)
            pass
        return status


class OperatorForm(forms.ModelForm):
    class Meta:
        model = Operator
        fields = ['name', 'role', 'shift', 'is_active']
