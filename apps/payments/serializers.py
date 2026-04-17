from rest_framework import serializers
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    booking_id = serializers.IntegerField(source='booking.id', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'booking_id', 'amount', 'status',
            'reference', 'paid_at', 'created_at',
        ]
        read_only_fields = ['id', 'reference', 'created_at', 'paid_at']
        
class PaymentSimulationSerializer(serializers.Serializer):
    reference = serializers.CharField()