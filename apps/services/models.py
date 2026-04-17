from django.db import models

class Service(models,models):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    duration = models.PositiveBigIntegerField(help_text='Duration in minutes')
    
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text='Price in your local currency'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Inactive services are hidden from customers'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'services_service'
        ordering = ['name']
        
    def __str__(self):
        return f'{self.name} ({self.duration} mins - ${self.price})'