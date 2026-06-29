import tkinter as tk
from PIL import Image, ImageTk
from engine import load_songs, play_song, pause_song, resume_song, get_state, get_songs, get_current_song, is_favorite, add_favorite, remove_favorite, seek_song, get_recent,  get_position, previous_song, get_favorites, next_song
from io import BytesIO


# =========================================================
# ROOT
# =========================================================
root = tk.Tk()
root.title("Music Player")
root.geometry("400x470")

# =========================================================
# GLOBAL AREA
# =========================================================
current_play_button = None
last_page= None
def refresh_favorites():
    
    global current_play_button
    current_play_button=None
    for  widget in fav_frame.winfo_children():
        widget.destroy()

    for song in get_favorites():
        create_song_item(
            fav_frame,
            song["title"],
            song["artist"],
            song["genre"],
            song["album_art"],
            is_favorite(song),
            song["file"],
            get_favorites(),
            song["duration"])

def refresh_recent():
    for  widget in rec_frame.winfo_children():
        widget.destroy()

    for song in get_recent():
        create_song_item(
            rec_frame,
            song["title"],
            song["artist"],
            song["genre"],
            song["album_art"],
            is_favorite(song),
            song["file"],
            get_recent(),
            song["duration"])

def refresh_music():

    global current_play_button
    current_play_button= None

    for  widget in music_frame.winfo_children():
        widget.destroy()

    for song in get_songs():
        create_song_item(
            music_frame,
            song["title"],
            song["artist"],
            song["genre"],
            song["album_art"],
            is_favorite(song),
            song["file"],
            get_songs(),
            song["duration"])

def check_song_finished():
    global current_play_button
    state=get_state()

    if not state["playing"] and not state["paused"]:
        progress.set(0)
        current_time_label.config(text="0:00")
        play_btn.config(text="▶")
        if current_play_button:
            current_play_button.config(text="▶")
            current_play_button=None

    root.after(1000, check_song_finished)

# =========================================================
# COLORS 
# =========================================================
BG = "#F7E7E5"
WHITE = "#FFFFFF"
PINK = "#F1B7B3"
DARK = "#1F1F1F"
GREY = "#7D7D7D"
PEACH = "#FFD5C5"
ORANGE = "#FBB093"
LIGHT_PEACH = "#2596BE"

root.configure(bg=BG)

# =========================================================
# PAGE SYSTEM
# =========================================================
container = tk.Frame(root, bg=BG)
container.pack(fill="both", expand=True)

home = tk.Frame(container, bg=BG)
music = tk.Frame(container, bg=BG)
favorites = tk.Frame(container, bg=BG)
recent = tk.Frame(container, bg=BG)
now_playing = tk.Frame(container, bg=BG)

pages = [home, music, favorites, recent, now_playing]
for p in pages:
    p.place(relwidth=1, relheight=1)

def show(page):
    global last_page
    if page != now_playing:
        last_page = page
    page.tkraise()
    if page == music:
        refresh_music()
    elif page== favorites:
        refresh_favorites()
    elif page== recent:
        refresh_recent()

    if page==now_playing:
        nav.pack_forget() # hide nav
    else:
        nav.pack(side="bottom", fill="x")


# =========================================================
# NOW PLAYING
# =========================================================

# COLLAPSE BUTTON

def go_back():
    show(last_page) 

back_btn = tk.Button(
    now_playing,
    text="⌄",
    fg=PINK,
    bg=BG,
    bd=0,
    font=("Arial", 20, "bold"),
    command=go_back
)
back_btn.pack(anchor="w", padx=10, pady=(5, 0))

# ALBUM ART

album_frame = tk.Frame(now_playing, bg=WHITE, width=200, height=200)
album_frame.pack(pady=(5, 8))
album_frame.pack_propagate(False)

img = Image.open("album_art.png").resize((200, 200))
photo = ImageTk.PhotoImage(img)

album_label = tk.Label(album_frame, image=photo, bg=WHITE)
album_label.image = photo
album_label.pack()

# SONG INFO

song_label = tk.Label(now_playing, text="Song Title",
                      bg=BG, fg=DARK,
                      font=("Arial", 14, "bold"))
song_label.pack(pady=(5, 2))

artist_label = tk.Label(now_playing, text="Artist Name",
                        bg=BG, fg=GREY,
                        font=("Arial", 10))
artist_label.pack()

genre_label = tk.Label(now_playing, text="POP / R&B",
                       bg=BG, fg=ORANGE,
                       font=("Arial", 9, "bold"))
genre_label.pack(pady=(2, 8))


# CONTROLS

controls = tk.Frame(now_playing, bg=BG)
controls.pack(pady=(0, 5))



def toggle_play():
    state=get_state()
    if state["playing"]:
        pause_song()
        play_btn.config(text="▶")
        
    elif state["paused"]:
        resume_song()
        play_btn.config(text="⏸")

    elif state["song"]:
        play_song(
            state["song"],
            state["playlist"]
            )
        play_btn.config(text="⏸")

btn_style = {
    "bd": 0,
    "font": ("Arial", 18, "bold"),
    "width": 3,
    "height": 1
}


def go_previous():
    song = previous_song()

    if song:
        show_now_playing(
            song["title"],
            song["artist"],
            song["genre"],
            song["album_art"]
            )
        play_btn.config(text="⏸")


prev_btn=tk.Button(controls, text="⏮", bg=PEACH, fg=ORANGE, command=go_previous, **btn_style)
prev_btn.grid(row=0, column=0, padx=10)

play_btn = tk.Button(controls, text="⏸" if get_state()["playing"] else "▶",
                     bg=PINK, fg="white",
                     command=toggle_play,
                     **btn_style)
play_btn.grid(row=0, column=1, padx=10)


def go_next():
    
    song=next_song()
    
    if song:
        show_now_playing(
            song["title"],
            song["artist"],
            song["genre"],
            song["album_art"]
            )
        play_btn.config(text="⏸")


next_btn= tk.Button(controls, text="⏭", bg=PEACH, fg=ORANGE, command=go_next, **btn_style)
next_btn.grid(row=0, column=2, padx=10)

# SEEK BAR

seek_frame = tk.Frame(now_playing, bg=BG)
seek_frame.pack(fill="x", padx=20, pady=(15, 10))

current_time_label = tk.Label(
    seek_frame,
    text="0:00",
    bg=BG,
    fg=GREY
)
current_time_label.pack(side="left")

progress = tk.Scale(
    seek_frame,
    from_=0,
    to=0,
    orient="horizontal",
    length=180,
    bg=BG,
    troughcolor=PINK,
    highlightthickness=0,
    showvalue=False
)
progress.pack(side="left", fill="x", expand=True, padx=5)
progress.bind("<ButtonRelease-1>", lambda e: seek_song(progress.get()))

duration_label = tk.Label(
    seek_frame,
    text="0:00",
    bg=BG,
    fg=GREY
)
duration_label.pack(side="right")

def format_time(seconds):
    minutes = int(seconds//60)
    seconds= int(seconds % 60)
    return f"{minutes}:{seconds:02}"

def update_progress():
    state=get_state()
    if state["playing"] and state["song"]:
        current = get_position()
       
        progress.set(current)

        current_time_label.config(text=format_time(current))
        duration_label.config(text=format_time(state["song"]["duration"]))

    root.after(1000, update_progress)

# =========================================================
# SCROLL SYSTEM
# =========================================================
def make_scroll(parent):
    canvas = tk.Canvas(parent, bg=BG, highlightthickness=0)
    scrollbar = tk.Scrollbar(parent, command=canvas.yview)

    frame = tk.Frame(canvas, bg=BG)

    canvas.create_window((0, 0), window=frame, anchor="nw", width=380)
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    frame.bind("<Configure>",
               lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    return frame

music_frame = make_scroll(music)
fav_frame = make_scroll(favorites)
rec_frame = make_scroll(recent)

# =========================================================
# CLICKABLE FRAME SYSTEM
# =========================================================
def clickable(widget, command):
    widget.bind("<Button-1>", lambda e: command())
    for child in widget.winfo_children():
        child.bind("<Button-1>", lambda e: command())

# =========================================================
# SHOW NOW PLAYING
# =========================================================

def show_now_playing(title, artist, genre, album_art):

    song_label.config(text=title)
    artist_label.config(text=artist)
    genre_label.config(text=genre)
    
    song=get_state()["song"]
    progress.config(to=song.get("duration", 0))
    progress.set(0)

    if get_state()["playing"]:
        play_btn.config(text="⏸")
    else:
        play_btn.config(text="▶")
        

    if album_art:
        img = Image.open(BytesIO(album_art)).resize((200, 200))
        photo = ImageTk.PhotoImage(img)

        album_label.config(image=photo)
        album_label.image = photo

    show(now_playing)

# =========================================================
# SONG ITEM TEMPLATE 
# =========================================================

def create_song_item(parent, title, artist, genre, album_art=None, is_favorite=False, file_path=None, playlist=None, duration=None ):
 
    current_song=get_current_song()
    global current_play_button 

    item = tk.Frame(parent, bg=WHITE, height=80)
    item.pack(fill="x", padx=10, pady=5)
    item.pack_propagate(False)

    # ---------------- IMAGE ----------------
    if album_art:
        img=Image.open(BytesIO(album_art)).resize((55,55))
    else:
        img = Image.open("album.png").resize((55, 55))
    photo = ImageTk.PhotoImage(img)

    art = tk.Label(item, image=photo, bg=WHITE)
    art.image = photo
    art.pack(side="left", padx=8)

    # ---------------- TEXT ----------------
    text = tk.Frame(item, bg=WHITE)
    text.pack(side="left", fill="both", expand=True)

    title_label=tk.Label(text, text=title,
             bg=WHITE, fg=DARK,
             font=("Arial", 10, "bold"))
    title_label.pack(anchor="w")

    artist_label=tk.Label(text, text=artist,
             bg=WHITE, fg=GREY,
             font=("Arial", 8))
    artist_label.pack(anchor="w")

    genre_label=tk.Label(text, text=genre,
             bg=WHITE, fg=PEACH,
             font=("Arial", 8, "italic"))
    genre_label.pack(anchor="w")

    # ---------------- ACTIONS ----------------
    action = tk.Frame(item, bg=WHITE)
    action.pack(side="right", padx=5)

    def toggle_heart():

        song_data = {
            "title" : title,
            "artist" : artist, 
            "genre" : genre, 
            "album_art" : album_art, 
            "file" : file_path,
            "duration": duration
            }

        if song_data in get_favorites():
            remove_favorite(song_data)
            heart.config(fg="black")
        else:
            add_favorite(song_data)
            heart.config(fg=PINK)

        refresh_favorites()
        refresh_music()


    heart_color = PINK if is_favorite else "black"
    heart = tk.Button(action, text="❤", bg=WHITE,
                      fg=heart_color, bd=0, font=("Arial", 14), command=toggle_heart)
    heart.pack(side="left")

    def toggle_play():

        global current_play_button

        song={
            "title" : title,
            "artist" : artist,
            "genre" : genre,
            "album_art" : album_art,
            "file" : file_path,
            "duration": duration
            }
        if play.cget("text")=="▶":
            for widget in parent.winfo_children():
                for child in widget.winfo_children():
                    if isinstance(child, tk.Frame):
                        for btn in child.winfo_children():
                            if isinstance(btn, tk.Button):
                                if btn.cget("text")=="⏸":
                                    btn.config(text="▶")

            play_song(song, playlist)
            play.config(text="⏸")
            current_play_button=play
          
        else:
            pause_song()
            play.config(text="▶")
            current_play_button=None

    play_text="▶"

    state= get_state()
    if current_song and current_song["file"]==file_path and state["playing"]:
        play_text="⏸"

    play = tk.Button(action, text=play_text, bg=WHITE,
                     fg="black", bd=0, font=("Arial", 14),command=toggle_play)
    play.pack(side="left")

    def on_frame_click():

        global current_play_button

        song = {
            "title": title,
            "artist": artist,
            "genre": genre,
            "album_art": album_art,
            "file": file_path,
            "duration": duration
        }

        current_song = get_current_song()
        state=get_state()
        if current_song==song and state["paused"]:
            resume_song()
            play.config(text="⏸")
            current_play_button = play

        elif current_song != song:

            if current_play_button and current_play_button != play:
                current_play_button.config(text="▶")

            print(song)
            play_song(song, playlist)

            play.config(text="⏸")

            current_play_button = play

        show_now_playing(title, artist, genre, album_art)
     

    clickable(item, on_frame_click)


# =========================================================
# FAVORITES PAGE ITEMS 
# =========================================================
def create_fav_item():

    item = tk.Frame(fav_frame, bg=WHITE, height=80)
    item.pack(fill="x", padx=10, pady=5)
    item.pack_propagate(False)

    img = Image.open("favorites.png").resize((55, 55))
    photo = ImageTk.PhotoImage(img)

    tk.Label(item, image=photo, bg=WHITE).pack(side="left", padx=8)
    item.image = photo

    create_song_item(fav_frame, "Favorite Song", "Artist • Genre")

# =========================================================
# RECENT PAGE ITEMS (USES recent.png)
# =========================================================
def create_recent_item():

    item = tk.Frame(rec_frame, bg=WHITE, height=80)
    item.pack(fill="x", padx=10, pady=5)
    item.pack_propagate(False)

    img = Image.open("recent.png").resize((55, 55))
    photo = ImageTk.PhotoImage(img)

    tk.Label(item, image=photo, bg=WHITE).pack(side="left", padx=8)
    item.image = photo

songs= load_songs()   
for song in songs:
    create_song_item(music_frame, song["title"], song["artist"],song["genre"], song["album_art"], is_favorite(song), song["file"])


# =========================================================
# DISCOVER (HOME)
# =========================================================
tk.Label(home, text="Discover",
         bg=BG, fg=DARK,
         font=("Arial", 18, "bold")).pack(pady=15)

def open_fav():
    show(favorites)

def open_recent():
    show(recent)

def discover_card(parent, image_file, text, command):

    card = tk.Frame(parent, bg=WHITE, height=150)
    card.pack(fill="x", padx=12, pady=10)
    card.pack_propagate(False)

    img = Image.open(image_file).resize((100, 100))
    photo = ImageTk.PhotoImage(img)

    img_label = tk.Label(card, image=photo, bg=WHITE)
    img_label.image = photo
    img_label.pack(side="left", padx=10)

    tk.Label(card, text=text,
             bg=WHITE, fg=DARK,
             font=("Arial", 14, "bold")).pack(side="left")

    clickable(card, command)

discover_card(home, "favorites.png", "Favorites", open_fav)
discover_card(home, "recent.png", "Recent", open_recent)

# =========================================================
# NAVIGATION 
# =========================================================
nav = tk.Frame(root, bg=WHITE, height=55)
nav.pack(side="bottom", fill="x")
nav.pack_propagate(False)

def nav_button(text, page, color):
    tk.Button(nav, text=text, bg=color, fg="white",
              bd=0, font=("Arial", 14, "bold"),
              command=lambda: show(page)
    ).pack(side="left", expand=True, fill="both")

nav_button("🏠 Discover", home, PEACH)
nav_button("🎵 Music", music, PINK)

# =========================================================
# START
# =========================================================

check_song_finished()
update_progress()
show(home)
root.mainloop()