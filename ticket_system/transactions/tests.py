from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from setup.models import Customer, Area, Item, Machine, Operator
from .models import JobOrder, SalesOrder, PrintingTransaction

import datetime

class TransactionStrictTest(TestCase):
    def setUp(self):
        self.area = Area.objects.create(name="Production")
        self.customer = Customer.objects.create(name="Client X", area=self.area)
        self.machine = Machine.objects.create(name="Printer A", area=self.area)
        self.operator = Operator.objects.create(name="Worker 1", role="Printer", shift="Day")
        
        self.so = SalesOrder.objects.create(
            order_number="SO-001",
            customer=self.customer,
            order_date=timezone.now().date(),
            delivery_date=timezone.now().date() + datetime.timedelta(days=10)
        )
        self.so.approve() # Status -> Approved

        self.job = JobOrder.objects.create(
            sales_order=self.so,
            order_date=timezone.now().date(),
            due_date=timezone.now().date() + datetime.timedelta(days=5),
        )

    def test_sales_order_date_validation(self):
        """Test delivery date cannot be before order date"""
        so = SalesOrder(
            order_number="SO-BAD-DATE",
            customer=self.customer,
            order_date=timezone.now().date(),
            delivery_date=timezone.now().date() - datetime.timedelta(days=1)
        )
        with self.assertRaisesMessage(ValidationError, "Delivery date cannot be before Order date"):
             so.full_clean()

    def test_printing_mass_balance(self):
        """Test Input >= Output + Waste"""
        # Case 1: Valid
        tx = PrintingTransaction.objects.create(
             date=timezone.now().date(),
             job_order=self.job,
             machine=self.machine,
             operator=self.operator,
             input_mat_kg=100.0,
             printed_kg=90.0,
             wastage_kg=5.0
        )
        # Case 2: Invalid (90 + 15 > 100)
        tx_bad = PrintingTransaction(
             date=timezone.now().date(),
             job_order=self.job,
             machine=self.machine,
             operator=self.operator,
             input_mat_kg=100.0,
             printed_kg=90.0,
             wastage_kg=15.0
        )
        with self.assertRaisesMessage(ValidationError, "Input Material cannot be less than Printed + Wastage"):
            tx_bad.save()
