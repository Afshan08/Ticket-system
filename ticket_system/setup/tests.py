from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import Area, Customer, ItemCategory, Item, Machine, Operator

class AreaModelTest(TestCase):
    def setUp(self):
        self.area = Area.objects.create(name="Press Room", status=Area.Status.ACTIVE)

    def test_prevent_deactivation_if_dependent(self):
        """Test cannot deactivate area if active customer exists"""
        Customer.objects.create(name="Dep Client", area=self.area, status=Customer.Status.ACTIVE)
        self.area.status = Area.Status.INACTIVE
        with self.assertRaisesMessage(ValidationError, "Cannot deactivate Area with active customers"):
            self.area.save()

class CustomerModelTest(TestCase):
    def setUp(self):
        self.area = Area.objects.create(name="Zone A")
        self.customer = Customer.objects.create(
            name="Acme Corp",
            area=self.area,
            customer_type=Customer.CustomerType.BUSINESS
        )

    def test_create_customer(self):
        self.assertEqual(self.customer.customer_type, 'business')

class ItemModelTest(TestCase):
    def setUp(self):
        self.cat = ItemCategory.objects.create(name="Papers")
        
    def test_negative_dimensions(self):
        """Test that negative dimensions raise error"""
        item = Item(
            name="Bad Paper", 
            category=self.cat, 
            gsm=-10,
            unit_price=10
        )
        with self.assertRaisesMessage(ValidationError, "Dimensions cannot be negative"):
            item.full_clean() # explicit full_clean needed if using .create() usually validates but negative decimal 

class MachineModelTest(TestCase):
    def setUp(self):
        self.area = Area.objects.create(name="Machine Hall")
        self.machine = Machine.objects.create(name="Heidelberg XL", area=self.area)

    def test_negative_speed(self):
        self.machine.speed_capacity = -500
        with self.assertRaisesMessage(ValidationError, "Speed capacity cannot be negative"):
            self.machine.save()
