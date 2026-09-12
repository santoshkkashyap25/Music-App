from django.urls import path
from . import views

app_name = 'music'

urlpatterns = [
    # Albums
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('album/add/', views.AlbumCreate.as_view(), name='album-add'),
    path('album/<int:pk>/edit/', views.AlbumUpdate.as_view(), name='album-update'),
    path('album/<int:pk>/delete/', views.AlbumDelete.as_view(), name='album-delete'),
    path('album/<int:pk>/favorite/', views.toggle_album_favorite, name='album-favorite'),

    # Songs
    path('songs/', views.SongsView.as_view(), name='songs'),
    path('album/<int:pk>/song/add/', views.SongCreate.as_view(), name='song-add'),
    path('song/<int:pk>/delete/', views.SongDelete.as_view(), name='song-delete'),
    path('song/<int:pk>/favorite/', views.toggle_song_favorite, name='song-favorite'),

    # Authentication
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
]
