from django.test import TestCase
from master_data.models import Unit, Buyer, Item, Operation, OperationRate, Size, Designation
from erp_core.models import Employee
from master_data.logic import get_operation_rate
from decimal import Decimal
import datetime

class RateResolutionTest(TestCase):
    def setUp(self):
        self.unit = Unit.objects.create(name="Test Unit")
        self.buyer = Buyer.objects.create(name="Nike")
        self.item = Item.objects.create(name="T-Shirt")
        self.operation = Operation.objects.create(name="Hemming")
        self.size_xl = Size.objects.create(name="XL")
        self.size_l = Size.objects.create(name="L")
        self.dept = self.unit.departments.create(name="Test Dept")
        self.desig = Designation.objects.create(name="Test Desig")
        self.emp = Employee.objects.create(
            employee_id="EMP_RATE", full_name="Rate Test", gender="M",
            unit=self.unit, department=self.dept, designation=self.desig,
            salary_type="PRODUCTION_WISE", rate=Decimal('5.00') # Fallback rate
        )

    def test_rate_priority(self):
        # 1. Buyer + Operation (No Item/Size)
        OperationRate.objects.create(
            buyer=self.buyer, item=self.item, operation=self.operation,
            rate=Decimal('10.00'), unit=self.unit,
            effective_from=datetime.date(2023, 1, 1), is_active=True
        )
        
        # Should pick Buyer+Item+Op rate (since we didn't specify size)
        rate = get_operation_rate(self.unit.id, self.buyer.id, self.item.id, self.operation.id, date=datetime.date(2023, 10, 1))
        self.assertEqual(rate, Decimal('10.00'))

        # 2. Add Buyer + Item + Operation + Size
        OperationRate.objects.create(
            buyer=self.buyer, item=self.item, operation=self.operation, size=self.size_xl,
            rate=Decimal('12.00'), unit=self.unit,
            effective_from=datetime.date(2023, 1, 1), is_active=True
        )
        
        rate = get_operation_rate(self.unit.id, self.buyer.id, self.item.id, self.operation.id, size_id=self.size_xl.id, date=datetime.date(2023, 10, 1))
        self.assertEqual(rate, Decimal('12.00'))

        # 3. Fallback to Employee Rate (when no specific rate found)
        rate = get_operation_rate(self.unit.id, self.buyer.id, self.item.id, self.operation.id, size_id=self.size_l.id, date=datetime.date(2023, 10, 1))
        # Logic says if size-specific not found, fallback to Buyer+Op. 
        # But we have Buyer+Item+Op (without size). Let's check logic.
        self.assertEqual(rate, Decimal('10.00')) # Fallback to Buyer+Item+Op
