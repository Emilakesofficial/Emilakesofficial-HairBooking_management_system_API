import logging
from datetime import timedelta
from django.db import transaction
from django.utils import timezone

from apps.availability.models import AvailabilitySlot
from apps.availability.cache import invalidate_availability_cache
from apps.bookings.models import Bookings
from apps.payments.models import Payment
from apps.notifications.tasks import (
    send_booking_confirmation,
    send_appointment_reminder,
    expire_unpaid_booking,
)
from django.conf import settings

logger = logging.getLogger(__name__)

class BookingValidationError(Exception):
    pass

class BookingService:
    @staticmethod
    def create_booking(
        customer_name: str,
        customer_phone: str,
        service_id: int,
        slot_id: int,
        notes: str = '',
    ) -> Bookings:
        with transaction.atomic():
            try:
                slot = AvailabilitySlot.objects.select_for_update().get(
                    id=slot_id,
                    is_available=True,
                )
            except AvailabilitySlot.DoesNotExist:
                raise BookingValidationError(
                    'This time slot is not longer available. Please choose another.'
                )
                
            booking = Bookings.objects.create(
                customer_name=customer_name,
                customer_phone=customer_phone,
                service_id=service_id,
                slot=slot,
                notes=notes,
                status=Bookings.Status.PENDING,
            )
            
            slot.is_available = False
            slot.save(update_fields=['is_available', 'updated_at'])
            
            payment = Payment.objects.create(
                booking=booking,
                amount=booking.service.price,
                status=Payment.Status.PENDING,
            )
            
            logger.info(
                f'Booking #{booking.id} created for {customer_name}'
                f'| Slot: {slot} | Payment ref: {payment.reference}'
            )
            
            invalidate_availability_cache()
            
            BookingService._schedule_tasks(booking, payment)
            return booking
        
    @staticmethod
    def _schedule_tasks(booking: Bookings, payment: Payment):
        expiry_minutes = getattr(settings, 'BOOKING_EXPIRY_MINUTES', 30)
        reminder_hours = getattr(settings, 'REMINDER_HOURS_BEFORE', 24)
        
        send_booking_confirmation.delay(booking.id)
        
        expire_unpaid_booking.apply_async(
            args=[booking.id],
            countdown=expiry_minutes * 60,  # Convert to seconds
        )
        
        appointment_dt = timezone.make_aware(
            booking.appointment_datetime,
            timezone.get_current_timezone()
        )
        reminder_eta = appointment_dt - timedelta(hours=reminder_hours)
        
        if reminder_eta > timezone.now():
            send_appointment_reminder.apply_async(
                args=[booking.id],
                eta=reminder_eta,
            )
            logger.info(
                f'Reminder scheduled for booking #{booking.id} at {reminder_eta}'
            )
            
    @staticmethod
    def expire_booking(booking_id: int):
        with transaction.atomic():
            try: 
                booking = Bookings.objects.select_for_update().get(
                    id=booking_id,
                    status=Bookings.Status.PENDING,
                )
            except Bookings.DoesNotExist:
                logger.info(
                    f'Expiry task: Booking #{booking_id} not in PENDING state. Skipping.'
                )
                return
            
            booking.status = Bookings.Status.EXPIRED
            booking.save(update_fields=['status', 'updated_at'])
            
            try:
                booking.payment.status = Payment.Status.FAILED
                booking.payment.save(update_fields=['status', 'updated_at'])
            except Payment.DoesNotExist:
                pass
            
            booking.slot.is_available = True
            booking.slot.save(update_fields=['is_available', 'updated_at'])
            
            logger.info(
                f'Booking #{booking_id} expired - slot {booking.slot_id} released.'
            )
            
            invalidate_availability_cache()
            
        @staticmethod
        def confirm_booking(booking_id: int) -> Bookings:
            with transaction.atomic():
                try:
                    booking = Bookings.objects.select_for_update().get(
                        id=booking_id,
                        status=Bookings.Status.PENDING,
                    )
                except Bookings.DoesNotExist:
                    raise BookingValidationError(
                        'Booking cannot be confirmed = it may already be confirmed or expired.'
                    )
                booking.status = Bookings.Status.CONFIRMED
                booking.save(update_fields=['status', 'updated_at'])
                
                payment = booking.payment
                payment.status = Payment.Status.PAID
                payment.paid_at = timezone.now()
                payment.save(update_fields=['status', 'paid_at', 'updated_at'])
                
            logger.info(f'Booking #{booking_id} confirmed - payment received.')
            return booking