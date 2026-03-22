from rest_framework import serializers
from .models import ProductionEntry, CuttingLog
from master_data.logic import get_operation_rate

class ProductionEntrySerializer(serializers.ModelSerializer):
    employee_name = serializers.ReadOnlyField(source='employee.full_name')
    buyer_name = serializers.ReadOnlyField(source='buyer.name')
    item_name = serializers.ReadOnlyField(source='item.name')
    operation_name = serializers.ReadOnlyField(source='operation.name')
    size_name = serializers.ReadOnlyField(source='size.name')

    class Meta:
        model = ProductionEntry
        fields = '__all__'
        read_only_fields = ('total_amount',)

    def validate(self, data):
        # Auto-fetch rate if not provided or to ensure accuracy
        if 'rate' not in data or not data['rate']:
            rate = get_operation_rate(
                unit_id=data['unit'].id,
                buyer_id=data['buyer'].id,
                item_id=data['item'].id,
                operation_id=data['operation'].id,
                size_id=data['size'].id if data.get('size') else None,
                date=data['date']
            )
            if rate is None:
                # Fallback to employee rate
                rate = data['employee'].rate
            
            if rate is None:
                raise serializers.ValidationError("Rate could not be resolved for this production entry.")
            
            data['rate'] = rate
        return data

class CuttingLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = CuttingLog
        fields = '__all__'
