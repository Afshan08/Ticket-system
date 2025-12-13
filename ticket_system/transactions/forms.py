from django import forms
from django.core.exceptions import ValidationError
from .models import (
    SalesOrder, JobOrder, PrintingTransaction, RewindingTransaction, 
    SlittingTransaction, LaminationTransaction, CoreTransaction
)
from setup.models import Customer, Machine, Operator

class SalesOrderForm(forms.ModelForm):
    class Meta:
        model = SalesOrder
        fields = ['customer', 'order_date', 'delivery_date', 'status', 'station', 
                  'category', 'type', 'customer_po_ref', 'po_date']
    
    def clean_status(self):
        status = self.cleaned_data.get('status')
        if self.instance.pk and self.instance.status == SalesOrder.Status.APPROVED:
             # Prevent editing if already approved (simplistic lock)
             # Real world: might allow some fields but not others.
             # Here we assume strict lock on status change via form unless special permission
             pass
        return status


class JobOrderForm(forms.ModelForm):
    class Meta:
        model = JobOrder
        fields = ['sales_order', 'order_date', 'due_date', 'priority', 'remarks', 'status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter SalesOrders to show only those that are Approved?
        # Requirement: "Prevent multiple JobOrders from same SalesOrder unless explicitly allowed"
        # We can implement this in clean() or filter queryset here.
        # self.fields['sales_order'].queryset = SalesOrder.objects.filter(status=SalesOrder.Status.APPROVED)
        pass


class PrintingTransactionForm(forms.ModelForm):
    class Meta:
        model = PrintingTransaction
        fields = ['date', 'job_order', 'machine', 'operator', 'start_time', 'end_time', 
                  'product_name', 'input_mat_kg', 'printed_kg', 'wastage_kg', 'total_output_qty', 'remarks']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter active operators
        self.fields['operator'].queryset = Operator.objects.filter(is_active=True)
        # Filter active machines
        self.fields['machine'].queryset = Machine.objects.filter(status='active')


class RewindingTransactionForm(forms.ModelForm):
    class Meta:
        model = RewindingTransaction
        fields = ['date', 'job_order', 'machine', 'operator', 'start_time', 'end_time', 
                  'input_weight', 'output_weight', 'wastage', 'actual_output', 'qc_notes', 'remarks']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['operator'].queryset = Operator.objects.filter(is_active=True)
        self.fields['machine'].queryset = Machine.objects.filter(status='active')


class SlittingTransactionForm(forms.ModelForm):
    class Meta:
        model = SlittingTransaction
        fields = ['date', 'job_order', 'machine', 'operator', 'start_time', 'end_time', 
                  'input_weight', 'target_width', 'output_pcs', 'waste_weight', 'remarks']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['operator'].queryset = Operator.objects.filter(is_active=True)
        self.fields['machine'].queryset = Machine.objects.filter(status='active')


class LaminationTransactionForm(forms.ModelForm):
    class Meta:
        model = LaminationTransaction
        fields = ['date', 'job_order', 'machine', 'operator', 'start_time', 'end_time', 
                  'plain_weight', 'printed_weight', 'laminated_weight', 'wastage', 'actual_output', 'qc_notes', 'remarks']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['operator'].queryset = Operator.objects.filter(is_active=True)
        self.fields['machine'].queryset = Machine.objects.filter(status='active')


class CoreTransactionForm(forms.ModelForm):
    class Meta:
        model = CoreTransaction
        fields = ['date', 'job_order', 'machine', 'operator', 'start_time', 'end_time', 
                  'before_weight', 'output_weight', 'wastage', 'actual_output', 'qc_notes', 'remarks']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['operator'].queryset = Operator.objects.filter(is_active=True)
        self.fields['machine'].queryset = Machine.objects.filter(status='active')