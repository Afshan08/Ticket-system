from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from setup.models import Customer, Item, Machine, Operator

class SalesOrder(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'Draft', _('Draft')
        APPROVED = 'Approved', _('Approved')
        IN_PRODUCTION = 'In Production', _('In Production')
        CLOSED = 'Closed', _('Closed')
        CANCELLED = 'Cancelled', _('Cancelled')

    order_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='sales_orders')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    order_date = models.DateField()
    delivery_date = models.DateField()
    
    # Metadata
    station = models.CharField(max_length=100, blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    type = models.CharField(max_length=100, blank=True, null=True)
    customer_po_ref = models.CharField(max_length=100, blank=True, null=True)
    po_date = models.DateField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sales_orders'

    def __str__(self):
        return self.order_number

    def clean(self):
        if self.delivery_date and self.order_date and self.delivery_date < self.order_date:
            raise ValidationError(_("Delivery date cannot be before Order date."))

    def approve(self):
        # Centralized state transition method
        if self.status != self.Status.DRAFT:
            raise ValidationError(_("Can only approve Draft orders."))
        self.status = self.Status.APPROVED
        self.save()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class SalesOrderLine(models.Model):
    sales_order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name='lines')
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    qty = models.DecimalField(max_digits=12, decimal_places=2)
    rate = models.DecimalField(max_digits=12, decimal_places=2)
    
    class Meta:
        db_table = 'sales_order_lines'
    
    def clean(self):
        if self.qty <= 0:
            raise ValidationError(_("Quantity must be positive."))
        if self.rate < 0:
             raise ValidationError(_("Rate cannot be negative."))


class JobOrder(models.Model):
    class Priority(models.TextChoices):
        MEDIUM = 'Medium', _('Medium')
        HIGH = 'High', _('High')
        LOW = 'Low', _('Low')

    class Status(models.TextChoices):
        PENDING = 'Pending', _('Pending')
        IN_PROGRESS = 'In Progress', _('In Progress')
        COMPLETED = 'Completed', _('Completed')
        CANCELLED = 'Cancelled', _('Cancelled')

    # Strict Link: One Job per SO (unless we want multiple, but requirement said STRICT link)
    sales_order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name='job_orders')
    
    # Derived from SO usually, but kept for scheduling flexibility
    order_date = models.DateField()
    due_date = models.DateField()
    
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.MEDIUM)
    remarks = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'job_orders'

    def __str__(self):
        return f"JO-{self.id} (SO: {self.sales_order.order_number})"

    def clean(self):
        if self.sales_order.status == SalesOrder.Status.DRAFT:
             raise ValidationError(_("Cannot create Job Order for a Draft Sales Order."))


class JobOrderItem(models.Model):
    job_order = models.ForeignKey(JobOrder, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    qty = models.DecimalField(max_digits=12, decimal_places=2)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'job_order_items'


class BaseTransaction(models.Model):
    """Abstract base class for all production transactions"""
    trans_no = models.AutoField(primary_key=True)
    date = models.DateField()
    job_order = models.ForeignKey(JobOrder, on_delete=models.PROTECT)
    machine = models.ForeignKey(Machine, on_delete=models.PROTECT)
    operator = models.ForeignKey(Operator, on_delete=models.PROTECT)
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def clean(self):
        if self.machine.status == Machine.Status.DISABLED:
            raise ValidationError(_("Selected machine is disabled."))
        if not self.operator.is_active:
             raise ValidationError(_("Selected operator is inactive."))
        
        # Validate User Logic: Input >= Output + Waste
        # Since field names differ per child model, we let child models call this or impl their own checks.

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class PrintingTransaction(BaseTransaction):
    product_name = models.CharField(max_length=200, blank=True, null=True)
    input_mat_kg = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    printed_kg = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    wastage_kg = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_output_qty = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        db_table = 'trans_printing'
        verbose_name = 'Printing Transaction'

    def clean(self):
        super().clean()
        if self.input_mat_kg < (self.printed_kg + self.wastage_kg):
            raise ValidationError(_("Input Material cannot be less than Printed + Wastage."))


class RewindingTransaction(BaseTransaction):
    input_weight = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    output_weight = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    wastage = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    actual_output = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    qc_notes = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'trans_rewinding'
    
    def clean(self):
        super().clean()
        if self.input_weight < (self.output_weight + self.wastage):
            raise ValidationError(_("Input weight cannot be less than Output + Wastage."))


class SlittingTransaction(BaseTransaction):
    input_weight = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    target_width = models.DecimalField(max_digits=10, decimal_places=2, help_text="Target Width (mm)", default=0)
    output_pcs = models.IntegerField(default=0)
    waste_weight = models.DecimalField(max_digits=10, decimal_places=2, help_text="Trim/Waste (Kg)", default=0)

    class Meta:
        db_table = 'trans_slitting'

    def clean(self):
        super().clean()
        # Slitting might not have direct 'output weight' field here (output_pcs is count),
        # but usually we'd want to track mass balance. Assuming waste_weight is usage.
        # Without explicit Output Kg field, we can't do exact balance check, 
        # but we can check if waste > input which is impossible.
        if self.waste_weight > self.input_weight:
             raise ValidationError(_("Waste cannot exceed Input weight."))


class LaminationTransaction(BaseTransaction):
    plain_weight = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    printed_weight = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    laminated_weight = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    wastage = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    actual_output = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    qc_notes = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'trans_lamination'
    
    def clean(self):
        super().clean()
        total_input = self.plain_weight + self.printed_weight
        if total_input < (self.laminated_weight + self.wastage):
             raise ValidationError(_("Total inputs (Plain+Printed) cannot be less than Output + Wastage."))


class CoreTransaction(BaseTransaction):
    before_weight = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    output_weight = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    wastage = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    actual_output = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    qc_notes = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'trans_core'

    def clean(self):
        super().clean()
        if self.before_weight < (self.output_weight + self.wastage):
            raise ValidationError(_("Input weight cannot be less than Output + Wastage."))