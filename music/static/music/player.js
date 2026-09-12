/**
 * WaveStream Audio Engine & Interactive Player Controller
 */

class WavePlayer {
    constructor() {
        this.audio = new Audio();
        this.queue = [];
        this.currentIndex = 0;
        this.isPlaying = false;
        this.isMuted = false;
        this.previousVolume = 0.8;
        this.isShuffle = false;
        this.isRepeat = false;

        // Web Audio fallback synthesizer
        this.synthCtx = null;
        this.synthInterval = null;
        this.synthOscillators = [];

        // DOM elements
        this.playerBar = document.getElementById('wavePlayerBar');
        this.playBtn = document.getElementById('playerPlayBtn');
        this.prevBtn = document.getElementById('playerPrevBtn');
        this.nextBtn = document.getElementById('playerNextBtn');
        this.shuffleBtn = document.getElementById('playerShuffleBtn');
        this.repeatBtn = document.getElementById('playerRepeatBtn');

        this.titleEl = document.getElementById('playerTrackTitle');
        this.artistEl = document.getElementById('playerTrackArtist');
        this.coverEl = document.getElementById('playerTrackCover');
        this.favBtn = document.getElementById('playerTrackFav');

        this.progressTrack = document.getElementById('playerProgressTrack');
        this.progressFill = document.getElementById('playerProgressFill');
        this.currTimeEl = document.getElementById('playerCurrentTime');
        this.durTimeEl = document.getElementById('playerDurationTime');

        this.volumeSlider = document.getElementById('playerVolumeSlider');
        this.volumeBtn = document.getElementById('playerVolumeBtn');

        this.init();
    }

    init() {
        // Setup initial volume
        this.audio.volume = 0.8;
        if (this.volumeSlider) this.volumeSlider.value = 0.8;

        // Audio element events
        this.audio.addEventListener('timeupdate', () => this.onTimeUpdate());
        this.audio.addEventListener('ended', () => this.onTrackEnded());
        this.audio.addEventListener('loadedmetadata', () => {
            if (this.durTimeEl && !isNaN(this.audio.duration)) {
                this.durTimeEl.textContent = this.formatTime(this.audio.duration);
            }
        });

        // Player Controls
        if (this.playBtn) this.playBtn.addEventListener('click', () => this.togglePlay());
        if (this.prevBtn) this.prevBtn.addEventListener('click', () => this.playPrevious());
        if (this.nextBtn) this.nextBtn.addEventListener('click', () => this.playNext());

        if (this.shuffleBtn) {
            this.shuffleBtn.addEventListener('click', () => {
                this.isShuffle = !this.isShuffle;
                this.shuffleBtn.classList.toggle('active', this.isShuffle);
            });
        }

        if (this.repeatBtn) {
            this.repeatBtn.addEventListener('click', () => {
                this.isRepeat = !this.isRepeat;
                this.repeatBtn.classList.toggle('active', this.isRepeat);
            });
        }

        // Progress scrubbing
        if (this.progressTrack) {
            this.progressTrack.addEventListener('click', (e) => this.seekTo(e));
        }

        // Volume controls
        if (this.volumeSlider) {
            this.volumeSlider.addEventListener('input', (e) => {
                const vol = parseFloat(e.target.value);
                this.setVolume(vol);
            });
        }

        if (this.volumeBtn) {
            this.volumeBtn.addEventListener('click', () => this.toggleMute());
        }

        // Bind document click handlers
        this.bindPageActions();

        // Check if page provided initial album queue
        const initialQueueEl = document.getElementById('initialQueueData');
        if (initialQueueEl) {
            try {
                const initialQueue = JSON.parse(initialQueueEl.textContent);
                if (initialQueue && initialQueue.length > 0) {
                    this.loadQueue(initialQueue, 0, false);
                }
            } catch (err) {
                console.warn("Could not parse initial queue:", err);
            }
        }
    }

    loadQueue(tracks, startIndex = 0, autoPlay = true) {
        if (!tracks || tracks.length === 0) return;
        this.queue = tracks;
        this.currentIndex = Math.max(0, Math.min(startIndex, tracks.length - 1));
        this.loadTrack(this.currentIndex, autoPlay);
    }

    loadTrack(index, autoPlay = true) {
        if (!this.queue[index]) return;
        const track = this.queue[index];

        this.stopSynthesizer();

        // Update UI info
        if (this.titleEl) this.titleEl.textContent = track.title || 'Unknown Title';
        if (this.artistEl) this.artistEl.textContent = track.artist || 'Unknown Artist';
        if (this.coverEl) {
            this.coverEl.onerror = () => {
                this.coverEl.onerror = null;
                this.coverEl.src = '/static/music/images/default_album.svg';
            };
            this.coverEl.src = track.cover || '/static/music/images/default_album.svg';
        }
        if (this.favBtn && track.id) {
            this.favBtn.setAttribute('data-id', track.id);
            this.updateFavIcon(this.favBtn, track.is_favorite);
        }

        // Reset progress bar
        if (this.progressFill) this.progressFill.style.width = '0%';
        if (this.currTimeEl) this.currTimeEl.textContent = '0:00';
        if (this.durTimeEl) this.durTimeEl.textContent = track.duration || '3:30';

        // Update active rows on page
        document.querySelectorAll('.track-row').forEach(row => {
            row.classList.remove('playing');
            if (row.getAttribute('data-id') == track.id) {
                row.classList.add('playing');
            }
        });

        // Set Audio source or use Synth fallback
        if (track.audio && track.audio.trim() !== "") {
            this.audio.src = track.audio;
            if (autoPlay) {
                this.audio.play().then(() => {
                    this.setPlayingState(true);
                }).catch(err => {
                    console.warn("Autoplay blocked or error loading audio:", err);
                    this.startSynthesizer();
                    this.setPlayingState(true);
                });
            }
        } else {
            // Track without audio file: use procedural synth
            this.audio.src = "";
            if (autoPlay) {
                this.startSynthesizer();
                this.setPlayingState(true);
            }
        }
    }

    togglePlay() {
        if (this.queue.length === 0) {
            // Check if there are any play buttons on page to grab
            const firstPlayBtn = document.querySelector('[data-action="play-track"], [data-action="play-album"]');
            if (firstPlayBtn) {
                firstPlayBtn.click();
                return;
            }
            return;
        }

        const currentTrack = this.queue[this.currentIndex];
        if (!currentTrack) return;

        if (this.isPlaying) {
            if (currentTrack.audio) {
                this.audio.pause();
            } else {
                this.stopSynthesizer();
            }
            this.setPlayingState(false);
        } else {
            if (currentTrack.audio) {
                this.audio.play().then(() => {
                    this.setPlayingState(true);
                }).catch(err => {
                    this.startSynthesizer();
                    this.setPlayingState(true);
                });
            } else {
                this.startSynthesizer();
                this.setPlayingState(true);
            }
        }
    }

    playNext() {
        if (this.queue.length === 0) return;
        if (this.isShuffle) {
            this.currentIndex = Math.floor(Math.random() * this.queue.length);
        } else {
            this.currentIndex = (this.currentIndex + 1) % this.queue.length;
        }
        this.loadTrack(this.currentIndex, true);
    }

    playPrevious() {
        if (this.queue.length === 0) return;
        if (this.audio.currentTime > 3) {
            this.audio.currentTime = 0;
            return;
        }
        this.currentIndex = (this.currentIndex - 1 + this.queue.length) % this.queue.length;
        this.loadTrack(this.currentIndex, true);
    }

    onTrackEnded() {
        if (this.isRepeat) {
            this.audio.currentTime = 0;
            this.audio.play();
        } else {
            this.playNext();
        }
    }

    seekTo(e) {
        const rect = this.progressTrack.getBoundingClientRect();
        const clickX = e.clientX - rect.left;
        const width = rect.width;
        const percent = Math.max(0, Math.min(1, clickX / width));

        if (!isNaN(this.audio.duration) && this.audio.duration > 0) {
            this.audio.currentTime = percent * this.audio.duration;
            if (this.progressFill) this.progressFill.style.width = `${percent * 100}%`;
        } else {
            // Synth preview scrub
            if (this.progressFill) this.progressFill.style.width = `${percent * 100}%`;
        }
    }

    onTimeUpdate() {
        if (isNaN(this.audio.duration) || this.audio.duration === 0) return;
        const current = this.audio.currentTime;
        const total = this.audio.duration;
        const percent = (current / total) * 100;

        if (this.progressFill) this.progressFill.style.width = `${percent}%`;
        if (this.currTimeEl) this.currTimeEl.textContent = this.formatTime(current);
        if (this.durTimeEl) this.durTimeEl.textContent = this.formatTime(total);
    }

    setVolume(vol) {
        this.audio.volume = vol;
        if (vol > 0) this.isMuted = false;
        this.updateVolumeIcon(vol);
    }

    toggleMute() {
        if (this.isMuted) {
            this.audio.volume = this.previousVolume || 0.8;
            if (this.volumeSlider) this.volumeSlider.value = this.audio.volume;
            this.isMuted = false;
        } else {
            this.previousVolume = this.audio.volume;
            this.audio.volume = 0;
            if (this.volumeSlider) this.volumeSlider.value = 0;
            this.isMuted = true;
        }
        this.updateVolumeIcon(this.audio.volume);
    }

    updateVolumeIcon(vol) {
        if (!this.volumeBtn) return;
        const icon = this.volumeBtn.querySelector('i');
        if (!icon) return;

        icon.className = '';
        if (vol === 0 || this.isMuted) {
            icon.className = 'fa-solid fa-volume-xmark';
        } else if (vol < 0.5) {
            icon.className = 'fa-solid fa-volume-low';
        } else {
            icon.className = 'fa-solid fa-volume-high';
        }
    }

    setPlayingState(playing) {
        this.isPlaying = playing;
        if (this.playBtn) {
            const icon = this.playBtn.querySelector('i');
            if (icon) {
                icon.className = playing ? 'fa-solid fa-pause' : 'fa-solid fa-play';
            }
        }
        if (this.playerBar) {
            this.playerBar.classList.toggle('playing', playing);
        }
    }

    /* =======================================================================
       Web Audio API Synthesizer Fallback (Generates Melodic Ambient Tones)
       ======================================================================= */
    startSynthesizer() {
        this.stopSynthesizer();
        try {
            const AudioCtx = window.AudioContext || window.webkitAudioContext;
            this.synthCtx = new AudioCtx();

            const notes = [261.63, 293.66, 329.63, 392.00, 440.00, 523.25]; // C, D, E, G, A, C
            let step = 0;
            let elapsedSec = 0;

            this.synthInterval = setInterval(() => {
                if (!this.isPlaying || !this.synthCtx) return;
                
                // Play chord note
                const freq = notes[step % notes.length];
                this.playSynthNote(freq);
                step++;
                elapsedSec += 1.5;

                // Update faux timeline
                if (this.currTimeEl) this.currTimeEl.textContent = this.formatTime(elapsedSec);
                if (this.progressFill) {
                    const pct = (elapsedSec / 210) * 100;
                    this.progressFill.style.width = `${Math.min(100, pct)}%`;
                }

                if (elapsedSec >= 210) {
                    this.onTrackEnded();
                }
            }, 1500);
        } catch (e) {
            console.warn("Web Audio Synthesizer not supported", e);
        }
    }

    playSynthNote(freq) {
        if (!this.synthCtx) return;
        const osc = this.synthCtx.createOscillator();
        const gain = this.synthCtx.createGain();

        osc.type = 'sine';
        osc.frequency.setValueAtTime(freq, this.synthCtx.currentTime);

        gain.gain.setValueAtTime(0.001, this.synthCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.12 * this.audio.volume, this.synthCtx.currentTime + 0.2);
        gain.gain.exponentialRampToValueAtTime(0.0001, this.synthCtx.currentTime + 1.4);

        osc.connect(gain);
        gain.connect(this.synthCtx.destination);

        osc.start();
        osc.stop(this.synthCtx.currentTime + 1.45);
    }

    stopSynthesizer() {
        if (this.synthInterval) {
            clearInterval(this.synthInterval);
            this.synthInterval = null;
        }
        if (this.synthCtx) {
            try { this.synthCtx.close(); } catch (e) {}
            this.synthCtx = null;
        }
    }

    formatTime(seconds) {
        if (isNaN(seconds)) return '0:00';
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
    }

    /* =======================================================================
       Document Interactions & Event Delegation
       ======================================================================= */
    bindPageActions() {
        document.addEventListener('click', (e) => {
            // 1. Play Track button
            const playTrackBtn = e.target.closest('[data-action="play-track"]');
            if (playTrackBtn) {
                e.preventDefault();
                e.stopPropagation();
                const trackData = {
                    id: playTrackBtn.getAttribute('data-id'),
                    title: playTrackBtn.getAttribute('data-title'),
                    artist: playTrackBtn.getAttribute('data-artist'),
                    cover: playTrackBtn.getAttribute('data-cover'),
                    audio: playTrackBtn.getAttribute('data-audio'),
                    duration: playTrackBtn.getAttribute('data-duration') || '3:30',
                    is_favorite: playTrackBtn.getAttribute('data-favorite') === 'true',
                };
                this.loadQueue([trackData], 0, true);
                return;
            }

            // 2. Play Album button
            const playAlbumBtn = e.target.closest('[data-action="play-album"]');
            if (playAlbumBtn) {
                e.preventDefault();
                e.stopPropagation();
                const albumQueueJson = playAlbumBtn.getAttribute('data-queue');
                if (albumQueueJson) {
                    try {
                        const tracks = JSON.parse(albumQueueJson);
                        if (tracks && tracks.length > 0) {
                            this.loadQueue(tracks, 0, true);
                            return;
                        }
                    } catch (err) {
                        console.warn("Failed to parse album queue:", err);
                    }
                }
                // Fallback: single album track representation
                const singleTrack = {
                    id: playAlbumBtn.getAttribute('data-id'),
                    title: playAlbumBtn.getAttribute('data-title'),
                    artist: playAlbumBtn.getAttribute('data-artist'),
                    cover: playAlbumBtn.getAttribute('data-cover'),
                    audio: '',
                    duration: '3:30',
                    is_favorite: false,
                };
                this.loadQueue([singleTrack], 0, true);
                return;
            }

            // 3. Favorite button (Album or Song)
            const favBtn = e.target.closest('[data-action="fav-album"], [data-action="fav-song"]');
            if (favBtn) {
                e.preventDefault();
                e.stopPropagation();
                this.toggleFavorite(favBtn);
                return;
            }

            // 4. Mobile hamburger toggle
            const mobileToggle = e.target.closest('#mobileNavToggle');
            if (mobileToggle) {
                const navLinks = document.getElementById('navLinks');
                if (navLinks) navLinks.classList.toggle('open');
                return;
            }
        });
    }

    toggleFavorite(btn) {
        const type = btn.getAttribute('data-action') === 'fav-album' ? 'album' : 'song';
        const id = btn.getAttribute('data-id');
        if (!id) return;

        const url = type === 'album' ? `/music/album/${id}/favorite/` : `/music/song/${id}/favorite/`;

        fetch(url, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            }
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                this.updateFavIcon(btn, data.is_favorite);
                // Also update matching buttons with same id across the page
                document.querySelectorAll(`[data-action="${btn.getAttribute('data-action')}"][data-id="${id}"]`).forEach(other => {
                    if (other !== btn) this.updateFavIcon(other, data.is_favorite);
                });
            }
        })
        .catch(err => {
            console.error("Favorite toggle failed:", err);
        });
    }

    updateFavIcon(btn, isFav) {
        const icon = btn.querySelector('i');
        if (!icon) return;

        if (isFav) {
            icon.className = 'fa-solid fa-heart';
            btn.classList.add('active-fav');
        } else {
            icon.className = 'fa-regular fa-heart';
            btn.classList.remove('active-fav');
        }
    }
}

// Initialize on DOMContentLoaded
document.addEventListener('DOMContentLoaded', () => {
    window.wavePlayer = new WavePlayer();

    // Auto dismiss toasts after 4 seconds
    setTimeout(() => {
        document.querySelectorAll('.toast-msg').forEach(t => {
            t.style.opacity = '0';
            t.style.transform = 'translateX(100%)';
            t.style.transition = 'all 0.4s ease';
            setTimeout(() => t.remove(), 400);
        });
    }, 4000);
});
