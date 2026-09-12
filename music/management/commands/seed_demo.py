import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.conf import settings
from music.models import Album, Song


DEMO_ALBUMS = [
    {
        "album_title": "Neon Horizons",
        "artist": "The Midnight Wave",
        "genre": "Synthwave",
        "is_favorite": True,
        "svg_colors": ("#ec4899", "#8b5cf6", "#3b82f6"),
        "songs": [
            {"title": "Sunset Boulevard", "duration": "4:12", "favorite": True},
            {"title": "Cyber Drive", "duration": "3:45", "favorite": False},
            {"title": "Echoes in the Neon", "duration": "5:01", "favorite": True},
            {"title": "Digital Nostalgia", "duration": "3:28", "favorite": False},
        ]
    },
    {
        "album_title": "Midnight Coffee",
        "artist": "Lofi Dreamer",
        "genre": "Lo-Fi",
        "is_favorite": True,
        "svg_colors": ("#f59e0b", "#d97706", "#78350f"),
        "songs": [
            {"title": "Rainy Window", "duration": "2:35", "favorite": True},
            {"title": "Warm Blanket", "duration": "2:50", "favorite": False},
            {"title": "Study at 2 AM", "duration": "3:15", "favorite": True},
            {"title": "Slow Breeze", "duration": "2:40", "favorite": False},
        ]
    },
    {
        "album_title": "Cosmic Symphony",
        "artist": "Stellar Ensemble",
        "genre": "Classical",
        "is_favorite": False,
        "svg_colors": ("#06b6d4", "#3b82f6", "#1d4ed8"),
        "songs": [
            {"title": "Andromeda Awakening", "duration": "6:14", "favorite": True},
            {"title": "Starlight Sonata", "duration": "4:42", "favorite": False},
            {"title": "Voyage Beyond", "duration": "5:30", "favorite": False},
        ]
    },
    {
        "album_title": "Pulse Velocity",
        "artist": "Hyperion Beat",
        "genre": "Electronic",
        "is_favorite": True,
        "svg_colors": ("#10b981", "#059669", "#047857"),
        "songs": [
            {"title": "Kinetic Energy", "duration": "3:52", "favorite": True},
            {"title": "Circuit Breaker", "duration": "4:18", "favorite": True},
            {"title": "Overdrive Bass", "duration": "3:34", "favorite": False},
        ]
    },
    {
        "album_title": "Rhythm & Soul",
        "artist": "Maya & The Grooves",
        "genre": "Pop",
        "is_favorite": False,
        "svg_colors": ("#f43f5e", "#e11d48", "#be123c"),
        "songs": [
            {"title": "Golden Hour", "duration": "3:21", "favorite": True},
            {"title": "Velvet Nights", "duration": "3:58", "favorite": False},
            {"title": "Dancing With Shadow", "duration": "3:44", "favorite": False},
        ]
    }
]


def make_album_svg(title, artist, colors):
    c1, c2, c3 = colors
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500" width="500" height="500">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{c1}"/>
      <stop offset="50%" stop-color="{c2}"/>
      <stop offset="100%" stop-color="{c3}"/>
    </linearGradient>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="10" stdDeviation="15" flood-color="#000" flood-opacity="0.5"/>
    </filter>
  </defs>
  <rect width="500" height="500" fill="url(#bg)"/>
  <circle cx="250" cy="250" r="180" stroke="rgba(255,255,255,0.15)" stroke-width="4" fill="none"/>
  <circle cx="250" cy="250" r="140" stroke="rgba(255,255,255,0.2)" stroke-width="2" fill="none"/>
  <circle cx="250" cy="250" r="100" stroke="rgba(255,255,255,0.25)" stroke-width="3" fill="none"/>
  <circle cx="250" cy="250" r="60" fill="rgba(0,0,0,0.4)" filter="url(#shadow)"/>
  <circle cx="250" cy="250" r="18" fill="#ffffff"/>
  <text x="250" y="420" font-family="'Segoe UI', Roboto, sans-serif" font-size="28" font-weight="bold" fill="#ffffff" text-anchor="middle" letter-spacing="1">{title}</text>
  <text x="250" y="455" font-family="'Segoe UI', Roboto, sans-serif" font-size="18" fill="rgba(255,255,255,0.85)" text-anchor="middle">{artist}</text>
</svg>"""


class Command(BaseCommand):
    help = "Seed database with high-quality demo albums and songs"

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding demo albums and songs...")


        for data in DEMO_ALBUMS:
            album, created = Album.objects.get_or_create(
                album_title=data["album_title"],
                artist=data["artist"],
                defaults={
                    "genre": data["genre"],
                    "is_favorite": data["is_favorite"],
                }
            )

            if not album.album_logo or not hasattr(album.album_logo, 'url'):
                svg_content = make_album_svg(data["album_title"], data["artist"], data["svg_colors"])
                filename = f"{data['album_title'].lower().replace(' ', '_')}.svg"
                album.album_logo.save(filename, ContentFile(svg_content.encode('utf-8')), save=True)

            if created or album.song_set.count() == 0:
                for s in data["songs"]:
                    Song.objects.get_or_create(
                        album=album,
                        song_title=s["title"],
                        defaults={
                            "duration": s["duration"],
                            "file_type": "mp3",
                            "is_favorite": s["favorite"],
                        }
                    )

        self.stdout.write(self.style.SUCCESS(f"Successfully seeded demo data! Total Albums: {Album.objects.count()}, Total Songs: {Song.objects.count()}"))
