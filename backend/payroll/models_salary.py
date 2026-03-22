from django.db import models
from master_data.models import Unit
from erp_core.models import Employee

class SalaryRecord(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    month = models.IntegerField()
    year = models.IntegerField()
    
    production_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    attendance_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    overtime_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    advance_deduction = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    gross_salary = models.DecimalField(max_digits=12, decimal_places=2)
    net_salary = models.DecimalField(max_digits=12, decimal_places=2)
    
    is_locked = models.BooleanField(default=False)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('employee', 'month', 'year')
        indexes = [
            models.Index(fields=['employee', 'month', 'year']),
            models.Index(fields=['unit', 'month', 'year']),
        ]

    def __str__(self):
        return f"{self.employee.full_name} - {self.month}/{self.year}"
