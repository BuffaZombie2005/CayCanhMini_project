"""Signals - tự động tạo UserProfile khi user mới đăng ký."""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Tạo UserProfile cho user mới."""
    if created:
        UserProfile.objects.get_or_create(user=instance, defaults={'role': 'user'})
