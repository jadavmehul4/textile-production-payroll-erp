from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Sum, Count
from .models import ProductionEntry, DailyProductionSummary

@receiver(post_save, sender=ProductionEntry)
def update_daily_summary(sender, instance, **kwargs):
    date = instance.date
    unit = instance.unit
    
    summary, created = DailyProductionSummary.objects.get_or_create(
        unit=unit,
        date=date
    )
    
    # Recalculate totals for the unit and date
    stats = ProductionEntry.objects.filter(unit=unit, date=date).aggregate(
        total_qty=Sum('quantity'),
        total_amt=Sum('total_amount'),
        emp_count=Count('employee', distinct=True)
    )
    
    summary.total_quantity = stats['total_qty'] or 0
    summary.total_amount = stats['total_amt'] or 0
    summary.employee_count = stats['emp_count'] or 0
    summary.save()
