
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('listener', 'Listener (Music Fan)'),
        ('artist', 'Artist / Creator (Musician, Singer, Producer)'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='listener')
    stage_name = models.CharField(max_length=250, blank=True, null=True)

    @property
    def is_artist(self):
        return self.role == 'artist' or self.user.is_staff or self.user.is_superuser

    def __str__(self):
        display = self.stage_name or self.user.username
        return f"{display} ({self.get_role_display()})"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)


class Album(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='albums')
    artist = models.CharField(max_length=250)
    album_title = models.CharField(max_length=250)
    genre = models.CharField(max_length=250)
    album_logo = models.FileField(upload_to='album_logos/', blank=True, null=True)
    is_favorite = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse('music:detail', kwargs={'pk': self.pk})

    @property
    def song_count(self):
        return self.song_set.count()

    def __str__(self):
        return f"{self.album_title} - {self.artist}"


class Song(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    song_title = models.CharField(max_length=250)
    file_type = models.CharField(max_length=10, default="mp3", blank=True)
    audio_file = models.FileField(upload_to='songs/', blank=True, null=True)
    duration = models.CharField(max_length=20, default="3:30", blank=True)
    is_favorite = models.BooleanField(default=False)

    def get_audio_url(self):
        if self.audio_file and hasattr(self.audio_file, 'url'):
            return self.audio_file.url
        return ""

    def __str__(self):
        return self.song_title
