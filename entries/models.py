from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid

class Book(models.Model):
    user = models.ForeignKey(User, related_name='books', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    cover_color = models.CharField(max_length=50, default="#18181b") # Default zinc-900
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class Entry(models.Model):
    user = models.ForeignKey(User, related_name='entries', on_delete=models.CASCADE)
    book = models.ForeignKey(Book, related_name='entries_in_book', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    share_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Entries"

    def __str__(self):
        return self.title

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    notify_email = models.CharField(max_length=500, blank=True, null=True, help_text="Emails to notify (comma-separated for multiple friends)")
    notify_phone = models.CharField(max_length=20, blank=True, null=True, help_text="Phone number to notify (e.g., +91...)")

    def __str__(self):
        return f"{self.user.username}'s Profile"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        Profile.objects.create(user=instance)

class ReadEvent(models.Model):
    entry = models.ForeignKey(Entry, related_name='read_events', on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    duration_seconds = models.IntegerField(default=0)
    is_notified = models.BooleanField(default=False)

    def __str__(self):
        return f"Read for {self.entry.title} - {self.duration_seconds}s"
