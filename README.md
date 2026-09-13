# WaveStream

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0+-092E20.svg?style=flat&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![Live Demo](https://img.shields.io/badge/Live_Demo-Render-46E3B7.svg?style=flat&logo=render&logoColor=white)](https://wavestream-music.onrender.com/music/)

WaveStream is a self-hosted music catalog and web streaming application built with **Django 5** and **vanilla ES6 JavaScript**. It features an interactive persistent audio player, album and track management, role-based permissions (Artists vs. Listeners), and a modern dark interface inspired by modern streaming services.

The project is fully containerized with **Docker** for easy local and cloud deployment.

> **🚀 Live Demo**: [https://wavestream-music.onrender.com/music/](https://wavestream-music.onrender.com/music/)


---

## Table of Contents

- [Overview](#overview)
- [Screenshots](#screenshots)
- [Key Features](#key-features)
- [Architecture & Tech Stack](#architecture--tech-stack)
- [Prerequisites](#prerequisites)
- [Local Setup (Virtualenv)](#local-setup-virtualenv)
- [Running with Docker](#running-with-docker)
- [User Roles & Permissions](#user-roles--permissions)
- [Testing](#testing)


---

## Overview

WaveStream started as a classic Django music library project and was rebuilt into a full-featured web app with a responsive dark glassmorphic design, client-side player state management, and containerized deployment workflows.


---

## 📸 Screenshots

| **Home Library & Audio Player** | **Album Details & Tracklist** |
|:---:|:---:|
| ![Home Library](docs/screenshots/01_home_library.png) | ![Album Details](docs/screenshots/02_album_detail.png) |
| **Global Songs Catalogue** | **Creator Studio (Add Album)** |
| ![Songs Catalogue](docs/screenshots/03_songs_catalogue.png) | ![Add Album](docs/screenshots/04_add_album.png) |

---

## Key Features

- **🎧 Persistent Audio Player**: Full playback controls (play/pause, seek scrub bar, shuffle, repeat, volume, mute) and animated equalizer.
- **🎹 Dual Audio Engine**: Streams uploaded audio (`.mp3`, `.wav`) with procedural Web Audio synthesizer fallback for demo tracks.
- **💿 Catalog Management**: Full CRUD for albums and tracklists with live client-side artwork preview.
- **🔍 Search & Genre Filters**: Real-time multi-field search and quick genre filter pills (Synthwave, Lo-Fi, Electronic, Classical, Pop).
- **❤️ Instant AJAX Favorites**: One-click async favoriting for tracks and albums without page reloads.
- **👥 Role-Based Access Control**: Creator/Artist accounts manage albums and uploads; Listener accounts browse, stream, and favorite.
- **🐳 Dockerized & Cloud Ready**: Production Gunicorn + WhiteNoise static compression with automatic PostgreSQL / SQLite switching and automated demo seeding.


---

## Architecture & Tech Stack

| Layer | Technology | Details |
|---|---|---|
| **Backend** | Python 3.11+, Django 5.x | MTV architecture, class-based views, Django Auth & ModelForms |
| **WSGI Server** | Gunicorn | Multi-worker HTTP server for production container runtime |
| **Static Serving** | WhiteNoise | Compressed, manifest-backed static asset delivery without an Nginx sidecar |
| **Database** | SQLite / PostgreSQL | Local file database with seamless `DATABASE_URL` PostgreSQL support |
| **Frontend** | Vanilla JavaScript (ES6+), HTML5, CSS3 | Custom dark glassmorphic theme, Web Audio API tone synthesis, zero heavy JS frameworks |
| **Container** | Docker & Docker Compose | Lightweight `python:3.11-slim` image, multi-arch support, non-buffered logging |

---

## Prerequisites


- **Python**: 3.11 or higher
- **pip**: Latest version
- *(Optional for containers)*: **Docker Desktop** / Docker Engine

---

## Local Setup (Virtualenv)

### 1. Clone the repository
```bash
git clone https://github.com/santoshkkashyap25/Music-App.git
cd Music-App
```

### 2. Create and activate a virtual environment
**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run database migrations
```bash
python manage.py migrate
```

### 5. Seed sample demo music (Recommended)
```bash
python manage.py seed_demo
```
*Seeds 5 albums across multiple genres with 17 tracks and procedural SVG vinyl covers.*

### 6. Run the local development server
```bash
python manage.py runserver 8000
```
Open your browser at [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

---

## Running with Docker

Run the containerized application using Docker Compose:

```bash
docker compose up --build -d
```

- Access the app at: **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**
- View logs: `docker compose logs -f`
- Stop the container: `docker compose down`


---

## User Roles & Permissions

| Role | Browse & Stream | Favorite Tracks / Albums | Create Albums | Upload Songs | Edit / Delete Own Albums |
|---|:---:|:---:|:---:|:---:|:---:|
| **Anonymous / Guest** | ✅ | ❌ *(Redirects to login)* | ❌ | ❌ | ❌ |
| **Listener** | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Artist / Creator** | ✅ | ✅ | ✅ | ✅ | ✅ |

To test roles:
- Register a new account at `/music/register/` and select **Listener** or **Artist / Creator**.
- When logged in as an Artist, you can access the "Add Album" button, upload custom cover art, and add tracks.
- Listeners see a clean streaming interface without management buttons.

---

## Testing

The project includes an automated test suite covering models, class-based views, search, role-based permissions, and AJAX favorite endpoints:

```bash
python manage.py test
```

Expected output:
```
Creating test database for alias 'default'...
............
----------------------------------------------------------------------
Ran 12 tests in ~1.5s

OK
Destroying test database for alias 'default'...
```
