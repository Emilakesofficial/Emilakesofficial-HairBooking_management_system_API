from django.db import models
from apps.services.models import Service
from apps.availability.models import AvailabilitySlot
from datetime import datetime
import pytz

class Bookings(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        CANCELLED = 'cancelled', 'Cancelled'
        EXPIRED = 'expired', 'Expired'
        
    customer_name = models.CharField(max_length=200)
    customer_phone = models.CharField(max_length=200)
    
    service = models.ForeignKey(
        Service,
        on_delete=models.PROTECT,
        related_name='bookings',
    )
    slot = models.OneToOneField(
        AvailabilitySlot,
        on_delete=models.PROTECT,
        related_name='booking',
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    
    notes = models.TextField(
        blank=True,
        help_text='Optional notes from the customer'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bookings_booking'
        ordering = ['-created_at']

    def __str__(self):
        return (
            f'Booking #{self.pk} — {self.customer_name} '
            f'({self.slot.date} {self.slot.start_time}) [{self.status}]'
        )

    @property
    def appointment_datetime(self):
        """Return a full datetime combining slot date and start_time."""
        return datetime.combine(self.slot.date, self.slot.start_time)
