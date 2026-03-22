from decimal import Decimal
from django.db.models import Sum
from django.db import transaction
from production.models import ProductionEntry
from attendance.models import Attendance
from .models import Advance
from .models_salary import SalaryRecord
import datetime

@transaction.atomic
def calculate_monthly_salary(employee, month, year):
    unit = employee.unit
    
    # 1. Production Total
    production_total = ProductionEntry.objects.filter(
        employee=employee,
        date__month=month,
        date__year=year
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')

    # 2. Attendance & OT
    attendance_records = Attendance.objects.filter(
        employee=employee,
        date__month=month,
        date__year=year
    )
    
    attendance_salary = Decimal('0')
    overtime_total = Decimal('0')
    
    if employee.salary_type in ['MONTHLY', 'DAILY']:
        days_worked = Decimal('0')
        for rec in attendance_records:
            if rec.status == 'PRESENT':
                days_worked += Decimal('1')
            elif rec.status == 'HALF_DAY':
                days_worked += Decimal('0.5')
        
        if employee.salary_type == 'MONTHLY':
            # Simplified: monthly rate / 30 * days_worked
            attendance_salary = (employee.rate / Decimal('30')) * days_worked
        else: # DAILY
            attendance_salary = employee.rate * days_worked

    # OT calculation (Simplified: employee rate / 8 * OT hours)
    total_ot_hours = attendance_records.aggregate(total=Sum('overtime_hours'))['total'] or Decimal('0')
    hourly_rate = employee.rate / Decimal('240') if employee.salary_type == 'MONTHLY' else employee.rate / Decimal('8')
    overtime_total = total_ot_hours * hourly_rate

    # 3. Advance Deduction
    # Find active advances and calculate deduction
    advances = Advance.objects.filter(employee=employee, is_fully_paid=False).order_by('date')
    advance_deduction = Decimal('0')
    
    # This logic would be more complex in production to handle EMI vs Auto
    for adv in advances:
        if adv.repayment_type == 'AUTO':
            deduct = min(adv.outstanding_balance, (production_total + attendance_salary + overtime_total) * Decimal('0.5')) # Cap at 50%
            advance_deduction += deduct
        elif adv.repayment_type == 'EMI':
            deduct = min(adv.outstanding_balance, adv.emi_amount)
            advance_deduction += deduct
            
    gross_salary = production_total + attendance_salary + overtime_total
    net_salary = gross_salary - advance_deduction

    salary_record, created = SalaryRecord.objects.update_or_create(
        employee=employee,
        month=month,
        year=year,
        defaults={
            'production_total': production_total,
            'attendance_salary': attendance_salary,
            'overtime_total': overtime_total,
            'advance_deduction': advance_deduction,
            'gross_salary': gross_salary,
            'net_salary': net_salary,
            'unit': unit,
            'is_locked': False
        }
    )
    
    return salary_record
