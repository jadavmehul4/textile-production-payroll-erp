from django.db import models
from master_data.models import Unit, Buyer, Item, Operation, Size
from erp_core.models import Employee

class ProductionEntry(models.Model):
    date = models.DateField(db_index=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, db_index=True)
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, db_index=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    so_number = models.CharField(max_length=100)
    operation = models.ForeignKey(Operation, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField()
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('employee', 'date', 'so_number', 'operation', 'size')
        indexes = [
            models.Index(fields=['unit', 'date']),
            models.Index(fields=['employee', 'date']),
            models.Index(fields=['buyer', 'date']),
        ]

    def save(self, *args, **kwargs):
        self.total_amount = self.quantity * self.rate
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee.full_name} - {self.so_number} - {self.quantity}"

class CuttingLog(models.Model):
    date = models.DateField()
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    so_number = models.CharField(max_length=100)
    size = models.ForeignKey(Size, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField()
    damage_quantity = models.IntegerField(default=0)
    efficiency_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)

    def __str__(self):
        return f"Cutting: {self.so_number} - {self.quantity}"

class DailyProductionSummary(models.Model):
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    date = models.DateField()
    total_quantity = models.IntegerField(default=0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    employee_count = models.IntegerField(default=0)

    class Meta:
        unique_together = ('unit', 'date')
        indexes = [
            models.Index(fields=['unit', 'date']),
        ]
