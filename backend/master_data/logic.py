from master_data.models import OperationRate
from django.db import models

def get_operation_rate(unit_id, buyer_id, item_id, operation_id, size_id=None, date=None):
    """
    Priority order:
    1. Buyer + Item + Operation + Size
    2. Buyer + Item + Operation
    3. Buyer + Operation
    4. (Fallback to employee rate - handled in production entry)
    """
    from datetime import date as dt_date
    if date is None:
        date = dt_date.today()

    # 1. Buyer + Item + Operation + Size
    if size_id:
        rate_obj = OperationRate.objects.filter(
            unit_id=unit_id,
            buyer_id=buyer_id,
            item_id=item_id,
            operation_id=operation_id,
            size_id=size_id,
            effective_from__lte=date,
            is_active=True
        ).filter(
            models.Q(effective_to__gte=date) | models.Q(effective_to__isnull=True)
        ).order_by('-effective_from').first()
        
        if rate_obj:
            return rate_obj.rate

    # 2. Buyer + Item + Operation
    rate_obj = OperationRate.objects.filter(
        unit_id=unit_id,
        buyer_id=buyer_id,
        item_id=item_id,
        operation_id=operation_id,
        size_id__isnull=True,
        effective_from__lte=date,
        is_active=True
    ).filter(
        models.Q(effective_to__gte=date) | models.Q(effective_to__isnull=True)
    ).order_by('-effective_from').first()

    if rate_obj:
        return rate_obj.rate

    # 3. Buyer + Operation (Item agnostic)
    rate_obj = OperationRate.objects.filter(
        unit_id=unit_id,
        buyer_id=buyer_id,
        operation_id=operation_id,
        size_id__isnull=True,
        effective_from__lte=date,
        is_active=True
    ).filter(
        models.Q(effective_to__gte=date) | models.Q(effective_to__isnull=True)
    ).order_by('-effective_from').first()

    if rate_obj:
        return rate_obj.rate

    return None
