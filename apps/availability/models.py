from django.db import models

class AvailabilitySlot(models.Model):
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    is_available = models.BooleanField(default=True, db_index=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'availability_slot'
        ordering = ['date', 'start_time']
        unique_together = [['date', 'start_time', 'end_time']]
        
    def __str__(self):
        status = 'Available' if self.is_available else 'Booked'
        return f'{self.date} {self.start_time} - {self.end_time} [{status}]'
