from django.test import TestCase
from master_data.models import Unit, Buyer, Item, Operation, OperationRate, Size, Designation
from erp_core.models import Employee
from production.models import ProductionEntry
from attendance.models import Attendance
from payroll.models import Advance
from payroll.engine import calculate_monthly_salary
from decimal import Decimal
import datetime

class SalaryEngineTest(TestCase):
    def setUp(self):
        self.unit = Unit.objects.create(name="Test Unit")
        self.buyer = Buyer.objects.create(name="Test Buyer")
        self.item = Item.objects.create(name="Test Item")
        self.operation = Operation.objects.create(name="Test Op")
        self.size = Size.objects.create(name="L")
        
        self.dept = self.unit.departments.create(name="Test Dept")
        self.desig = Designation.objects.create(name="Test Desig")
        
        self.employee = Employee.objects.create(
            employee_id="EMP001",
            full_name="John Doe",
            gender="M",
            unit=self.unit,
            department=self.dept,
            designation=self.desig,
            salary_type="PRODUCTION_WISE",
            rate=Decimal('100.00')
        )
        
        self.op_rate = OperationRate.objects.create(
            buyer=self.buyer,
            item=self.item,
            operation=self.operation,
            size=self.size,
            rate=Decimal('10.00'),
            unit=self.unit,
            effective_from=datetime.date(2023, 1, 1),
            is_active=True
        )

    def test_salary_calculation(self):
        # Create Production
        ProductionEntry.objects.create(
            date=datetime.date(2023, 10, 15),
            employee=self.employee,
            buyer=self.buyer,
            item=self.item,
            so_number="SO001",
            operation=self.operation,
            size=self.size,
            quantity=100,
            rate=Decimal('10.00'),
            unit=self.unit
        )
        
        # Create Advance
        Advance.objects.create(
            employee=self.employee,
            date=datetime.date(2023, 10, 1),
            amount=Decimal('500.00'),
            unit=self.unit,
            repayment_type='AUTO'
        )
        
        salary_rec = calculate_monthly_salary(self.employee, 10, 2023)
        
        self.assertEqual(salary_rec.production_total, Decimal('1000.00'))
        self.assertEqual(salary_rec.advance_deduction, Decimal('500.00'))
        self.assertEqual(salary_rec.net_salary, Decimal('500.00'))
