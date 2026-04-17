from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models 
from .managers import UserManager

class User(AbstractBaseUser, PermissionsMixin):
    class Roles(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        HAIRSTYLIST = 'hairstylist', 'Hairstylist'
        
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=159)
    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.HAIRSTYLIST,
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    objects = UserManager()
    
    class Meta:
        db_table = 'accounts_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        
    def __str__(self):
        return f'{self.email} {self.get_role_display()}'
    
    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()
    
    
class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    phone = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)
    profile_photo = models.ImageField(
        upload_to='profiles/',
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'accounts_profile'
        
    def __str__(self):
        return f'Profile: {self.user.full_name}'