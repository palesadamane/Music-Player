import os
import pygame

from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3


# =========================================================
# AUDIO SETUP
# =========================================================

pygame.mixer.init()


# =========================================================
# ENGINE STATE
# =========================================================

songs = []

current_song = None
current_playlist = None
current_index = 0
seek_offset=0
favorites_playlist = []
recent_playlist = []

is_playing = False
is_paused = False



# =========================================================
# LOAD SONGS
# =========================================================

def load_songs():

    global songs

    songs = []

    for file in os.listdir("music"):

        if not file.endswith(".mp3"):
            continue

        path = os.path.join("music", file)

        try:

            audio = MP3(path, ID3=EasyID3)

            title = audio.get("title", [file])[0]
            artist = audio.get("artist", ["Unknown Artist"])[0]
            genre = audio.get("genre", ["Unknown Genre"])[0]


            album_art = None

            tags = ID3(path)

            for tag in tags.values():

                if tag.FrameID == "APIC":
                    album_art = tag.data
                    break

            song = {
                "title": title,
                "artist": artist,
                "genre": genre,
                "file": path,
                "album_art": album_art,
                "duration": audio.info.length
            }


            songs.append(song)


        except Exception as e:

            print("Error reading:", file)
            print(e)

    return songs

def get_songs():
    return songs


# =========================================================
# PLAY MUSIC
# =========================================================

def play_song(song, playlist):

    global current_song
    global current_playlist
    global current_index
    global is_playing
    global is_paused
    global seek_offset

    if current_song == song and is_paused:
        pygame.mixer.music.unpause()
        is_playing=True
        is_paused=False

        return
    current_song = song
    current_playlist = playlist
    seek_offset = 0


    if song in playlist:

        current_index = playlist.index(song)


    pygame.mixer.music.load(song["file"])

    pygame.mixer.music.play()


    is_playing = True
    is_paused = False


    add_recent(song)




# =========================================================
# PAUSE / RESUME / STOP
# =========================================================

def pause_song():

    global is_playing
    global is_paused


    pygame.mixer.music.pause()

    is_playing = False
    is_paused = True




def resume_song():

    global is_playing
    global is_paused


    pygame.mixer.music.unpause()

    is_playing = True
    is_paused = False




def stop_song():

    global is_playing
    global is_paused


    pygame.mixer.music.stop()

    is_playing = False
    is_paused = False




# =========================================================
# PLAYBACK STATE
# =========================================================

def get_current_song():
    return current_song



def get_current_playlist():

    return current_playlist



def get_state():
    global is_playing
    global is_paused

    if is_playing and not pygame.mixer.music.get_busy():
        is_playing=False
        is_paused=False


    return {
        "song": current_song,
        "playlist": current_playlist,
        "playing": is_playing,
        "paused": is_paused
    }

# =========================================================
# FAVORITES
# =========================================================

def add_favorite(song):

    if song not in favorites_playlist:

        favorites_playlist.append(song)


def remove_favorite(song):

    if song in favorites_playlist:

        favorites_playlist.remove(song)


def get_favorites():

    return favorites_playlist


def is_favorite(song):

    return song in favorites_playlist


# =========================================================
# RECENTS
# =========================================================

def add_recent(song):

    if song in recent_playlist:

        recent_playlist.remove(song)

    recent_playlist.insert(0, song)


def get_recent():

    return recent_playlist




# =========================================================
# NEXT SONG
# =========================================================

def next_song():

    global current_index


    if current_playlist is None:

        return None

    if current_index < len(current_playlist) - 1:

        current_index += 1
    else:
        current_index=0

    play_song(
            current_playlist[current_index],
            current_playlist
        )
    return current_song



# =========================================================
# PREVIOUS SONG
# =========================================================

def previous_song():

    global current_index

    if current_playlist is None:

        return None

    if current_index > 0:

        current_index -= 1
    else:
        current_index=len(current_playlist) -1

    play_song(
            current_playlist[current_index],
            current_playlist
        )
    return current_song




def get_position():

    return seek_offset + (pygame.mixer.music.get_pos() / 1000)

# =========================================================
# SEEK SONG
# =========================================================

def seek_song(position):
    global seek_offset
    global is_playing
    global is_paused

    seek_offset = position

    if current_song:
        pygame.mixer.music.play(
            start = position
            )
        if is_paused:
            pygame.mixer.music.pause()
            is_playing=False
            is_paused= True
        else:
            is_playing= True
            is_paused =False



# =========================================================
# RESET
# =========================================================

def reset():

    global current_song
    global current_playlist
    global current_index
    global is_playing
    global is_paused
    global seek_offset

    seek_offset=0

    pygame.mixer.music.stop()


    current_song = None
    current_playlist = None
    current_index = 0

    is_playing = False
    is_paused = False