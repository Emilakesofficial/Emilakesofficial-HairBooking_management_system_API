from rest_framework import serializers
from .models import Bookings
from apps.services.serializers import ServiceSerializer
from apps.availability.serializers import AvailabilitySlotSerializer

class BookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookings
        fields = [
            'id', 'customer_name', 'customer_phone',
            'service', 'slot', 'notes',
        ]
        read_only_fields = ['id']
        
    def validate_customer_phone(self, value):
        # Basic phone serialization - strip spaces and dashes
        cleaned = value.replace(' ', '').replace('-', '')
        if not cleaned.lstrip('+').isdigit():
            raise serializers.ValidationError('Phone number must contain only digits, spaces, dashes, oor a leading +.')
        if len(cleaned) < 11:
            raise serializers.ValidationError('Phone number is too short.')
        return cleaned
    
class BookingDetailSerializer(serializers.ModelSerializer):
    service = ServiceSerializer(read_only=True)
    slot = AvailabilitySlotSerializer(read_only=True)
    payment_reference = serializers.SerializerMethodField()
    
    class Meta:
        model = Bookings
        fields = [
            'id', 'customer_name', 'customer_phone',
            'service', 'slot', 'status', 'notes',
            'payment_reference', 'created_at',
        ]

    def get_payment_reference(self, obj):
        # Safely return payment reference if payment exists
        try:
            return obj.payment.reference
        except Exception:
            return None