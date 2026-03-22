from django.db import models
from master_data.models import Unit
from erp_core.models import Employee
from .models_salary import SalaryRecord

class Advance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField(blank=True, null=True)
    approved_by = models.ForeignKey('authentication.User', on_delete=models.SET_NULL, null=True)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    
    repayment_type = models.CharField(max_length=20, choices=(('AUTO', 'Auto'), ('EMI', 'EMI'), ('MANUAL', 'Manual')), default='AUTO')
    emi_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    outstanding_balance = models.DecimalField(max_digits=10, decimal_places=2)
    is_fully_paid = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.outstanding_balance = self.amount
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee.full_name} - {self.amount} on {self.date}"
