# 🎵 WaveStream — Modern Music Web Application

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.0+-092E20?style=for-the-badge&logo=django&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![CSS3](https://img.shields.io/badge/CSS3-Modern%20Dark%20Glass-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

A sleek, modern music streaming and catalog management web application built with **Django 5**, vanilla ES6 JavaScript, and a custom **Dark Glassmorphism** design system.

---

## ✨ Features

- **🎧 Persistent Bottom Audio Player**:
  - Interactive scrub seek bar with elapsed & total duration display (`mm:ss`).
  - Play, Pause, Next, Previous, Shuffle, and Repeat modes.
  - Volume slider with one-click Mute/Unmute toggle.
  - Animated sound visualizer equalizers synchronized with active playback.
- **🎹 Built-in Procedural Web Audio Synthesizer**:
  - Built-in fallback tone engine using the browser's Web Audio API so every track makes harmonious ambient sound immediately, even without manual MP3 uploads.
- **💿 Comprehensive Album & Track Management**:
  - Add, edit, and delete albums with high-res cover art.
  - Instant client-side image preview on upload.
  - Tracklist management: add tracks directly to albums with custom duration and audio files.
- **🔍 Real-Time Search & Multi-Criteria Filtering**:
  - Search bar searching across album titles, artist names, genres, and track titles.
  - Quick genre pills (Synthwave, Lo-Fi, Electronic, Classical, Pop, etc.).
- **❤️ Instant AJAX Favorites**:
  - One-click heart toggling for albums and songs with animated transitions without jarring page reloads.
- **🎨 Modern Dark Glassmorphism UI**:
  - Premium dark theme inspired by Spotify and Apple Music.
  - Modern typography powered by Google Fonts (*Outfit* and *Inter*).
  - Responsive layout with desktop header and mobile slide-out navigation.
- **🔐 User Authentication**:
  - Complete user registration, login, and logout workflows.
- **🌱 Instant Demo Seeding**:
  - Built-in management command to seed rich sample albums, tracklists, and SVG vinyl artwork.

---

## 🏗️ Project Structure

```
Music-App/
├── manage.py                   # Django CLI utility
├── requirements.txt            # Project dependencies
├── db.sqlite3                  # Local SQLite database
├── media/                      # Uploaded album artwork and audio files
│   └── album_logos/
├── website/                    # Django project configuration
│   ├── settings.py             # App settings, media & static config
│   ├── urls.py                 # Root URL router & media serving
│   └── wsgi.py
└── music/                      # Music application
    ├── models.py               # Album & Song models
    ├── views.py                # Class-based & API views
    ├── urls.py                 # App routing
    ├── forms.py                # Django ModelForms
    ├── static/music/           # Frontend assets
    │   ├── style.css           # Custom dark glassmorphism design system
    │   ├── player.js           # Interactive audio player controller & synth
    │   └── images/             # Fallback SVG placeholders
    ├── templates/music/        # HTML templates
    │   ├── layout.html         # Base shell with navbar & bottom player
    │   ├── index.html          # Album grid & genre filters
    │   ├── detail.html         # Album tracklist & song upload panel
    │   ├── songs.html          # Global songs catalogue
    │   ├── album_form.html     # Add / Edit album form with live preview
    │   ├── login.html          # Sign-in portal
    │   └── register.html       # Account creation portal
    └── management/commands/    # Management utilities
        └── seed_demo.py        # Demo dataset seeder
```

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/santoshkkashyap25/Music-App.git
cd Music-App
```

### 2. Create and activate a virtual environment
**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Apply database migrations
```bash
python manage.py migrate
```

### 5. Seed sample demo albums & songs (Optional but Recommended)
```bash
python manage.py seed_demo
```

### 6. Run development server
```bash
python manage.py runserver
```

Open your browser at `http://127.0.0.1:8000/`.

---

## 🐳 Docker Deployment

### Run locally with Docker Compose
```bash
docker compose up --build
```
Open `http://localhost:8000` in your browser.

### Build and run standalone Docker container
```bash
# Build image
docker build -t music-app .

# Run container
docker run -p 8000:8000 -e DEBUG=True -e SECRET_KEY=your-secret-key music-app
```

---

## 🚀 Deploying to Render

### Method 1: Render Blueprint (Recommended)
1. Push your code to GitHub.
2. Log in to [Render Dashboard](https://dashboard.render.com/).
3. Click **New +** → **Blueprint**.
4. Connect your repository. Render will automatically detect `render.yaml` and configure the Web Service with Docker runtime, health checks, and environment variables.
5. Click **Apply**.

### Method 2: Manual Web Service Creation
1. Click **New +** → **Web Service**.
2. Select your repository.
3. Choose **Docker** as the Runtime.
4. Set Environment Variables:
   - `DEBUG`: `False`
   - `SECRET_KEY`: (Generate or provide a secure key)
   - `WEB_CONCURRENCY`: `2`
5. Click **Deploy Web Service**.

---

## 📸 Key Routes

| Route | Description |
|---|---|
| `/` or `/music/` | Main discovery library & album grid |
| `/music/<id>/` | Album details, tracklist, and add song panel |
| `/music/songs/` | Global tracks catalogue with instant play |
| `/music/album/add/` | Create a new album with cover image |
| `/music/login/` | User sign-in |
| `/music/register/` | User registration |

---

## 📄 License
This project is licensed under the MIT License.

