from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Custom User model with role-based access control.
    
    Roles:
    - Librarian (is_staff=True): Full access to manage books and users
    - Member (is_staff=False): Can view books and borrow/return books
    """
    ROLE_CHOICES = [
        ('librarian', 'Librarian'),
        ('member', 'Member'),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='member',
        help_text='User role determining API access permissions'
    )
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def is_librarian(self):
        """Check if user is a librarian"""
        return self.role == 'librarian' or self.is_staff
    
    @property
    def is_member(self):
        """Check if user is a member"""
        return self.role == 'member'
    
    def save(self, *args, **kwargs):
        """
        Auto-set is_staff based on role
        Librarians should have is_staff=True for Django admin access
        """
        if self.role == 'librarian':
            self.is_staff = True
        else:
            self.is_staff = False
        super().save(*args, **kwargs)

