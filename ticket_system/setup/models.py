from django.db import models

# Create your models here.
class AreaForm(models.Model):
    """Model for managing geographic/operational areas in the ERP system."""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('maintenance', 'Under Maintenance'),
    ]
    
    area_code = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        help_text="Auto-generated code (e.g., AREA-0001)"
    )
    
    areaname = models.CharField(
        max_length=100,
        help_text="Descriptive name for the operational area"
    )
    
    area_description = models.TextField(
        blank=True,
        null=True,
        help_text="Additional details about the area's purpose or characteristics"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        help_text="Current operational status of the area"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'areas'
        verbose_name = 'Area'
        verbose_name_plural = 'Areas'
        ordering = ['area_code']
    
    def __str__(self):
        return f"{self.area_code} - {self.areaname}"


class ItemDefinition(models.Model):
    SALESTAX_CHOICES = [
    ('GST', 'GST'),
    ('VAT', 'VAT'),
    ('EXEMPT', 'Exempt'),
    ]
    item_code = models.CharField(unique=True, max_length=50)
    item_name = models.CharField(max_length=250)
    specification = models.CharField(null=True, blank=True)
    base_item = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name="variants")
    item_category = models.ForeignKey('INVcategory', on_delete=models.CASCADE, related_name="items")
    salestax_type = models.CharField(max_length=50, choices=SALESTAX_CHOICES)
    unit_of_measure = models.ForeignKey('UnitOfMeasure', on_delete=models.SET_NULL, null=True, blank=True, related_name="items")
    description = models.TextField(null=True, blank=True, help_text="Detailed description of the item")
    std_cost = models.DecimalField(max_digits=12, decimal_places=2)
    important = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "item_definition"
        verbose_name = 'Item Definition'
        verbose_name_plural = 'Item Definition'
    
    
    def __str__(self):
        return self.item_name

    ## TODO: Have to write a Item Category Model

    ## TODO: Have to write a machine model

    ## TODO: Have to write a operator model

    class Customer(models.Model):
    """Comprehensive model for managing customer information in the ERP system."""
    
    CUSTOMER_TYPE_CHOICES = [
        ('individual', 'Individual'),
        ('business', 'Business'),
        ('government', 'Government'),
        ('non_profit', 'Non-Profit'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
        ('pending_approval', 'Pending Approval'),
    ]
    
    PAYMENT_TERMS_CHOICES = [
        ('net_15', 'Net 15'),
        ('net_30', 'Net 30'),
        ('net_45', 'Net 45'),
        ('net_60', 'Net 60'),
        ('cod', 'Cash on Delivery'),
        ('prepaid', 'Prepaid'),
    ]
    
    CURRENCY_CHOICES = [
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
        ('GBP', 'British Pound'),
        ('CAD', 'Canadian Dollar'),
        ('AUD', 'Australian Dollar'),
        ('JPY', 'Japanese Yen'),
        ('PKR', "Pakistani Rupees"),
    ]
    
    # Basic Information
    customer_id = models.IntegerField(
        unique=True,
        blank=True,
        null=True,
        help_text="Auto-generated if new"
    )
    
    customer_code = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        help_text="Auto-generated code (e.g., CUST-0001)"
    )
    
    customer_name = models.CharField(
        max_length=200,
        help_text="Official registered business or individual name"
    )
    
    customer_type = models.CharField(
        max_length=20,
        choices=CUSTOMER_TYPE_CHOICES,
        help_text="Type of customer"
    )
    
    # Contact Information
    contact_person_name = models.CharField(
        max_length=100,
        help_text="Main point of contact for the customer"
    )
    
    contact_email = models.EmailField(
        help_text="Primary email address"
    )
    
    contact_phone = models.CharField(
        max_length=12,
        validators=[RegexValidator(
            regex=r'^\+?[\d\s\-\(\)]+$',
            message='Enter a valid phone number'
        )],
        help_text="Primary contact phone number"
    )
    
    
    
    country = models.CharField(
        max_length=100,
        default='Pakistan',
        help_text="Country"
    )

    
    payment_terms = models.CharField(
        max_length=20,
        choices=PAYMENT_TERMS_CHOICES,
        default='net_30',
        help_text="Payment terms"
    )
    
    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='PKR',
        help_text="Preferred currency"
    )
    
    # Additional Information
    website = models.URLField(
        blank=True,
        null=True,
        help_text="Website URL"
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Any additional information about the customer"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        help_text="Customer status"
    )
    
    is_preferred = models.BooleanField(
        default=False,
        help_text="Preferred customer"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'customers'
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'
        ordering = ['customer_name']
    
    def __str__(self):
        return f"{self.customer_name} ({self.customer_id or 'New'})"