import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.views import generic, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from .models import Album, Song, UserProfile
from .forms import AlbumForm, SongForm, UserRegisterForm, UserLoginForm


class IndexView(generic.ListView):
    template_name = 'music/index.html'
    context_object_name = 'all_albums'

    def get_queryset(self):
        queryset = Album.objects.all().prefetch_related('song_set').order_by('-id')
        query = self.request.GET.get('q')
        genre = self.request.GET.get('genre')
        fav_filter = self.request.GET.get('filter')

        if query:
            queryset = queryset.filter(
                Q(album_title__icontains=query) |
                Q(artist__icontains=query) |
                Q(genre__icontains=query)
            ).distinct()

        if genre:
            queryset = queryset.filter(genre__iexact=genre)

        if fav_filter == 'favorites':
            queryset = queryset.filter(is_favorite=True)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_genres = Album.objects.values_list('genre', flat=True).distinct()
        # Clean unique genres
        genres_set = sorted(list({g.strip().capitalize() for g in all_genres if g and g.strip()}))
        context['genres'] = genres_set
        context['selected_genre'] = self.request.GET.get('genre', '')
        context['selected_filter'] = self.request.GET.get('filter', '')
        context['search_query'] = self.request.GET.get('q', '')
        context['total_albums'] = Album.objects.count()
        context['total_songs'] = Song.objects.count()
        
        # Robust check for creator status
        user = self.request.user
        is_creator = False
        if user.is_authenticated:
            if user.is_staff:
                is_creator = True
            elif hasattr(user, 'profile') and user.profile.is_artist:
                is_creator = True
        context['is_creator'] = is_creator
        
        return context


class SongsView(generic.ListView):
    template_name = 'music/songs.html'
    context_object_name = 'all_songs'

    def get_queryset(self):
        queryset = Song.objects.select_related('album').all().order_by('-id')
        query = self.request.GET.get('q')
        fav_filter = self.request.GET.get('filter')

        if query:
            queryset = queryset.filter(
                Q(song_title__icontains=query) |
                Q(album__album_title__icontains=query) |
                Q(album__artist__icontains=query) |
                Q(album__genre__icontains=query)
            ).distinct()

        if fav_filter == 'favorites':
            queryset = queryset.filter(is_favorite=True)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['selected_filter'] = self.request.GET.get('filter', '')
        return context


class DetailView(generic.DetailView):
    model = Album
    template_name = 'music/detail.html'
    context_object_name = 'album'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        album = self.object
        songs = album.song_set.all().order_by('id')
        context['songs'] = songs
        
        # Determine if current viewer has creator/staff rights to edit/manage tracks
        user = self.request.user
        context['is_owner'] = user.is_authenticated and (user.is_staff or (album.user and album.user == user))

        # Pre-build JSON tracklist data for the audio player
        queue = []
        for s in songs:
            queue.append({
                'id': s.id,
                'title': s.song_title,
                'artist': album.artist,
                'album': album.album_title,
                'cover': album.album_logo.url if album.album_logo else '/static/music/images/default_album.svg',
                'audio': s.get_audio_url(),
                'duration': s.duration or '3:30',
                'is_favorite': s.is_favorite,
            })
        context['album_queue_json'] = json.dumps(queue)
        context['song_form'] = SongForm()
        return context


class AlbumCreate(CreateView):
    model = Album
    form_class = AlbumForm
    template_name = 'music/album_form.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.info(request, "Please sign in as an Artist / Creator to publish albums.")
            return redirect('music:login')
        
        profile = getattr(request.user, 'profile', None)
        if not (request.user.is_staff or (profile and profile.is_artist)):
            messages.error(request, "Only registered Artists/Creators can publish albums. Listeners have streaming access!")
            return redirect('music:index')
            
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        if hasattr(self.request.user, 'profile') and self.request.user.profile.stage_name:
            initial['artist'] = self.request.user.profile.stage_name
        else:
            initial['artist'] = self.request.user.username
        return initial

    def form_valid(self, form):
        form.instance.user = self.request.user
        if not form.instance.artist:
            form.instance.artist = getattr(self.request.user.profile, 'stage_name', None) or self.request.user.username
        messages.success(self.request, f"Album '{form.instance.album_title}' published to your artist catalog!")
        return super().form_valid(form)


class AlbumUpdate(UpdateView):
    model = Album
    form_class = AlbumForm
    template_name = 'music/album_form.html'

    def dispatch(self, request, *args, **kwargs):
        album = self.get_object()
        if not request.user.is_authenticated or not (request.user.is_staff or (album.user and album.user == request.user)):
            messages.error(request, "You do not have permission to edit this album.")
            return redirect('music:detail', pk=album.pk)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, "Album updated successfully!")
        return super().form_valid(form)


class AlbumDelete(DeleteView):
    model = Album
    success_url = reverse_lazy('music:index')

    def dispatch(self, request, *args, **kwargs):
        album = self.get_object()
        if not request.user.is_authenticated or not (request.user.is_staff or (album.user and album.user == request.user)):
            messages.error(request, "You do not have permission to delete this album.")
            return redirect('music:detail', pk=album.pk)
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        messages.info(request, "Album removed from your catalog.")
        return super().post(request, *args, **kwargs)


class SongCreate(View):
    def post(self, request, pk):
        album = get_object_or_404(Album, pk=pk)
        if not request.user.is_authenticated or not (request.user.is_staff or (album.user and album.user == request.user)):
            messages.error(request, "Only the creator of this album can add tracks.")
            return redirect('music:detail', pk=album.pk)

        form = SongForm(request.POST, request.FILES)
        if form.is_valid():
            song = form.save(commit=False)
            song.album = album
            song.save()
            messages.success(request, f"Added track '{song.song_title}'!")
        else:
            messages.error(request, "Could not add song. Please check the fields.")
        return redirect('music:detail', pk=album.pk)


class SongDelete(View):
    def post(self, request, pk):
        song = get_object_or_404(Song, pk=pk)
        album = song.album
        if not request.user.is_authenticated or not (request.user.is_staff or (album.user and album.user == request.user)):
            messages.error(request, "You do not have permission to remove tracks from this album.")
            return redirect('music:detail', pk=album.pk)

        song_title = song.song_title
        song.delete()
        messages.info(request, f"Removed track '{song_title}'.")
        return redirect('music:detail', pk=album.pk)


def toggle_album_favorite(request, pk):
    album = get_object_or_404(Album, pk=pk)
    album.is_favorite = not album.is_favorite
    album.save()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
        return JsonResponse({'success': True, 'is_favorite': album.is_favorite, 'id': album.id})
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('music:index')))


def toggle_song_favorite(request, pk):
    song = get_object_or_404(Song, pk=pk)
    song.is_favorite = not song.is_favorite
    song.save()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
        return JsonResponse({'success': True, 'is_favorite': song.is_favorite, 'id': song.id})
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('music:index')))


def register_user(request):
    if request.user.is_authenticated:
        return redirect('music:index')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            # Save profile role and stage name
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.role = form.cleaned_data.get('role', 'listener')
            profile.stage_name = form.cleaned_data.get('stage_name', '').strip()
            profile.save()
            
            login(request, user)
            role_label = "Artist / Creator" if profile.is_artist else "Music Listener"
            messages.success(request, f"Welcome to WaveStream, {user.username}! Registered as {role_label}.")
            return redirect('music:index')
        else:
            messages.error(request, "Registration error. Please check the fields below.")
    else:
        form = UserRegisterForm()
    return render(request, 'music/register.html', {'form': form})


def login_user(request):
    if request.user.is_authenticated:
        return redirect('music:index')

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('music:index')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = UserLoginForm()
    return render(request, 'music/login.html', {'form': form})


def logout_user(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('music:index')