from rest_framework import serializers
from .models import Unit, Department, Designation, Buyer, Item, Operation, Size, OperationRate

class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = '__all__'

class DepartmentSerializer(serializers.ModelSerializer):
    unit_name = serializers.ReadOnlyField(source='unit.name')
    class Meta:
        model = Department
        fields = '__all__'

class DesignationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Designation
        fields = '__all__'

class BuyerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Buyer
        fields = '__all__'

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'

class OperationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operation
        fields = '__all__'

class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = '__all__'

class OperationRateSerializer(serializers.ModelSerializer):
    buyer_name = serializers.ReadOnlyField(source='buyer.name')
    item_name = serializers.ReadOnlyField(source='item.name')
    operation_name = serializers.ReadOnlyField(source='operation.name')
    size_name = serializers.ReadOnlyField(source='size.name')
    unit_name = serializers.ReadOnlyField(source='unit.name')
    class Meta:
        model = OperationRate
        fields = '__all__'
