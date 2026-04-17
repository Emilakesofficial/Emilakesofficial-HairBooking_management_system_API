# apps/payments/models.py

import uuid
from django.db import models
from apps.bookings.models import Booking


def generate_reference():
    """Generate a unique payment reference like HB-XXXX-XXXX."""
    suffix = uuid.uuid4().hex[:8].upper()
    return f'HB-{suffix[:4]}-{suffix[4:]}'


class Payment(models.Model):
    """
    Payment record linked to a booking.
    simulation
    """

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'        # Waiting for payment
        PAID = 'paid', 'Paid'                 # Payment received
        FAILED = 'failed', 'Failed'           # Payment attempt failed
        REFUNDED = 'refunded', 'Refunded'     # Payment was refunded

    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name='payment',
    )

    # Amount mirrors the service price at time of booking
    amount = models.DecimalField(max_digits=8, decimal_places=2)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )

    # Unique reference for tracking — auto-generated on creation
    reference = models.CharField(
        max_length=20,
        unique=True,
        default=generate_reference,
    )

    # Timestamp of when payment was completed (if applicable)
    paid_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payments_payment'
        ordering = ['-created_at']

    def __str__(self):
        return f'Payment {self.reference} — {self.status} (${self.amount})'