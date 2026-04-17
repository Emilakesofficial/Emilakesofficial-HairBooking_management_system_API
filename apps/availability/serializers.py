from rest_framework import serializers
from .models import AvailabilitySlot
from datetime import date

class AvailabilitySlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvailabilitySlot
        fields = [
            'id', 'date', 'start_time', 'end_time',
            'is_available', 'created_at',
        ]
        read_only_fields = ['id', 'is_available', 'created_at']
        
        def validate(self, attr):
            # ensure end_time is after start_time
            if attr['end_time'] <= attr['start_time']:
                raise serializers.ValidationError({'end_time': 'End time must be after start time.'})
            
            # ensure the slot is in the future
            if attr['data'] < date.today():
                raise serializers.ValidationError({'date': 'Cannot create availability slots in the past.'})
            return attr
        
    
                