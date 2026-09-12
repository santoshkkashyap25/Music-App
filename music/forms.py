from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import Album, Song


class AlbumForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = ['artist', 'album_title', 'genre', 'album_logo']
        widgets = {
            'artist': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Daft Punk, A.R. Rahman'}),
            'album_title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Discovery, Roar'}),
            'genre': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Electronic, Pop, Rock, Classical'}),
            'album_logo': forms.FileInput(attrs={'class': 'form-input-file', 'accept': 'image/*'}),
        }


class SongForm(forms.ModelForm):
    class Meta:
        model = Song
        fields = ['song_title', 'file_type', 'duration', 'audio_file']
        widgets = {
            'song_title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. One More Time'}),
            'file_type': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'mp3, wav, etc.'}),
            'duration': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. 3:45'}),
            'audio_file': forms.FileInput(attrs={'class': 'form-input-file', 'accept': 'audio/*'}),
        }


class UserRegisterForm(forms.ModelForm):
    ROLE_CHOICES = [
        ('listener', 'Listener — Browse, stream, search, and curate favorites'),
        ('artist', 'Artist / Creator — Publish albums, upload tracks, and manage catalog'),
    ]
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        initial='listener',
        widget=forms.RadioSelect(attrs={'class': 'role-radio-input'}),
        label="I want to join as a:"
    )
    stage_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. DJ Pulse, Luna Sky'}),
        label="Artist / Stage Name (Optional)"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Choose a strong password'})
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Confirm your password'}),
        label="Confirm Password"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Choose a username'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'you@example.com'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('password_confirm')
        if p1 and p2 and p1 != p2:
            self.add_error('password_confirm', "Passwords do not match.")
        return cleaned_data


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Password'}))