from rest_framework import serializers
from .models import Service

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = [
            'id', 'name', 'description',
            'duration', 'price', 'is_active',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']
        
    def validate_duration(self, value):
        if value < 15:
            raise serializers.ValidationError('Service duration must be at least 15 minutes')
        
        if value > 480:
            raise serializers.ValidationError('Service period must cannot exceed 8 hours')
        
        return value
    
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError('Price must be greater than zero.')
        return value
    