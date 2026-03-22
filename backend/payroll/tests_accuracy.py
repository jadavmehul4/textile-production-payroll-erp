from django.test import TestCase
from master_data.models import Unit, Buyer, Item, Operation, OperationRate, Size, Designation
from erp_core.models import Employee
from production.models import ProductionEntry
from attendance.models import Attendance
from payroll.models import Advance
from payroll.engine import calculate_monthly_salary
from decimal import Decimal
import datetime

class PayrollEngineAccuracyTest(TestCase):
    def setUp(self):
        self.unit = Unit.objects.create(name="Test Unit")
        self.buyer = Buyer.objects.create(name="Test Buyer")
        self.item = Item.objects.create(name="Test Item")
        self.operation = Operation.objects.create(name="Test Op")
        self.size = Size.objects.create(name="L")
        self.dept = self.unit.departments.create(name="Test Dept")
        self.desig = Designation.objects.create(name="Test Desig")

    def test_production_salary(self):
        emp = Employee.objects.create(
            employee_id="EMP001", full_name="John P", gender="M",
            unit=self.unit, department=self.dept, designation=self.desig,
            salary_type="PRODUCTION_WISE", rate=Decimal('0')
        )
        ProductionEntry.objects.create(
            date=datetime.date(2023, 10, 15), employee=emp, buyer=self.buyer,
            item=self.item, so_number="SO001", operation=self.operation,
            size=self.size, quantity=120, rate=Decimal('3.00'), unit=self.unit
        )
        salary_rec = calculate_monthly_salary(emp, 10, 2023)
        self.assertEqual(salary_rec.production_total, Decimal('360.00'))

    def test_monthly_salary_with_attendance(self):
        emp = Employee.objects.create(
            employee_id="EMP002", full_name="John M", gender="M",
            unit=self.unit, department=self.dept, designation=self.desig,
            salary_type="MONTHLY", rate=Decimal('15000.00')
        )
        # 24 days worked
        for d in range(1, 25):
            Attendance.objects.create(
                date=datetime.date(2023, 10, d), employee=emp,
                status='PRESENT', unit=self.unit
            )
        salary_rec = calculate_monthly_salary(emp, 10, 2023)
        # (15000 / 30) * 24 = 12000
        self.assertEqual(salary_rec.attendance_salary, Decimal('12000.00'))

    def test_overtime_pay(self):
        emp = Employee.objects.create(
            employee_id="EMP003", full_name="John OT", gender="M",
            unit=self.unit, department=self.dept, designation=self.desig,
            salary_type="DAILY", rate=Decimal('800.00') # 100 per hour
        )
        Attendance.objects.create(
            date=datetime.date(2023, 10, 1), employee=emp,
            status='PRESENT', overtime_hours=Decimal('10.00'), unit=self.unit
        )
        salary_rec = calculate_monthly_salary(emp, 10, 2023)
        # 800 + (800/8 * 10) = 800 + 1000 = 1800
        self.assertEqual(salary_rec.attendance_salary, Decimal('800.00'))
        self.assertEqual(salary_rec.overtime_total, Decimal('1000.00'))

    def test_advance_deduction(self):
        emp = Employee.objects.create(
            employee_id="EMP004", full_name="John Adv", gender="M",
            unit=self.unit, department=self.dept, designation=self.desig,
            salary_type="MONTHLY", rate=Decimal('30000.00')
        )
        for d in range(1, 11): # 10 days = 10000 salary
            Attendance.objects.create(
                date=datetime.date(2023, 10, d), employee=emp,
                status='PRESENT', unit=self.unit
            )
        Advance.objects.create(
            employee=emp, date=datetime.date(2023, 10, 1),
            amount=Decimal('3000.00'), unit=self.unit, repayment_type='AUTO'
        )
        salary_rec = calculate_monthly_salary(emp, 10, 2023)
        self.assertEqual(salary_rec.gross_salary, Decimal('10000.00'))
        self.assertEqual(salary_rec.advance_deduction, Decimal('3000.00'))
        self.assertEqual(salary_rec.net_salary, Decimal('7000.00'))
