from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from music.models import Album, Song, UserProfile


class MusicAppTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Create Artist User
        self.artist_user = User.objects.create_user(username="daft_artist", password="secretpassword123")
        self.artist_user.profile.role = 'artist'
        self.artist_user.profile.stage_name = "Daft Punk"
        self.artist_user.profile.save()

        # Create Listener User
        self.listener_user = User.objects.create_user(username="music_fan", password="secretpassword123")
        self.listener_user.profile.role = 'listener'
        self.listener_user.profile.save()

        # Create Album owned by artist
        self.album = Album.objects.create(
            user=self.artist_user,
            artist="Daft Punk",
            album_title="Discovery",
            genre="Electronic",
            is_favorite=False
        )
        self.song = Song.objects.create(
            album=self.album,
            song_title="One More Time",
            file_type="mp3",
            duration="5:20",
            is_favorite=False
        )

    def test_root_redirect(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith('/music/'))

    def test_index_view(self):
        response = self.client.get(reverse('music:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "WaveStream")
        self.assertContains(response, "Discovery")

    def test_detail_view(self):
        response = self.client.get(reverse('music:detail', kwargs={'pk': self.album.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "One More Time")

    def test_songs_view(self):
        response = self.client.get(reverse('music:songs'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "One More Time")

    def test_search(self):
        response = self.client.get(reverse('music:index') + '?q=Discovery')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Discovery")

    def test_toggle_album_favorite(self):
        response = self.client.get(
            reverse('music:album-favorite', kwargs={'pk': self.album.pk}),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.album.refresh_from_db()
        self.assertTrue(self.album.is_favorite)

    def test_toggle_song_favorite(self):
        response = self.client.get(
            reverse('music:song-favorite', kwargs={'pk': self.song.pk}),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.song.refresh_from_db()
        self.assertTrue(self.song.is_favorite)

    def test_listener_cannot_create_album(self):
        self.client.login(username="music_fan", password="secretpassword123")
        response = self.client.get(reverse('music:album-add'))
        self.assertEqual(response.status_code, 302)  # redirected to index

    def test_artist_can_create_album(self):
        self.client.login(username="daft_artist", password="secretpassword123")
        response = self.client.post(reverse('music:album-add'), {
            'album_title': 'Random Access Memories',
            'artist': 'Daft Punk',
            'genre': 'Electronic'
        })
        self.assertEqual(response.status_code, 302)
        new_album = Album.objects.filter(album_title='Random Access Memories').first()
        self.assertIsNotNone(new_album)
        self.assertEqual(new_album.user, self.artist_user)

    def test_owner_can_add_song(self):
        self.client.login(username="daft_artist", password="secretpassword123")
        response = self.client.post(
            reverse('music:song-add', kwargs={'pk': self.album.pk}),
            {'song_title': 'Harder, Better, Faster, Stronger', 'duration': '3:45', 'file_type': 'mp3'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.album.song_set.count(), 2)

    def test_listener_cannot_delete_song(self):
        self.client.login(username="music_fan", password="secretpassword123")
        response = self.client.post(reverse('music:song-delete', kwargs={'pk': self.song.pk}))
        self.assertEqual(response.status_code, 302)
        # Song should still exist
        self.assertEqual(Song.objects.filter(pk=self.song.pk).count(), 1)

    def test_owner_can_delete_song(self):
        self.client.login(username="daft_artist", password="secretpassword123")
        response = self.client.post(reverse('music:song-delete', kwargs={'pk': self.song.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Song.objects.filter(pk=self.song.pk).count(), 0)
