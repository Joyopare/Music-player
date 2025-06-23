import flet as ft
import os
import pygame
import time
import random
import threading
from mutagen.mp3 import MP3
import librosa
import numpy as np
import matplotlib.pyplot as plt

def generate_waveform(audio_path, output_path):
    y, sr = librosa.load(audio_path, sr=None)
    plt.figure(figsize=(10, 2))
    plt.plot(np.linspace(0, len(y)/sr, len(y)), y, color='b')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight', pad_inches=0, transparent=True)
    plt.close()

def main(page: ft.Page):
    music_files = []
    current_index = 0
    repeat = False
    shuffle = False

    def add_files(e):
        if e.files:
            for file in e.files:
                music_files.append(file.path)
                playlist.controls.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Row([
                                ft.Icon(ft.icons.MUSIC_NOTE, color=ft.colors.BLUE),
                                ft.Text(f"{len(music_files)}. {file.name}", size=14),
                            ]),
                            padding=10,
                            bgcolor=ft.colors.WHITE,
                            border_radius=5,
                            on_click=lambda _, idx=len(music_files)-1: select_song(idx)
                        )
                    )
                )
            page.update()

    def select_song(idx):
        nonlocal current_index
        current_index = idx
        play(None)

    def play(_):
        if not music_files:
            return
        try:
            pygame.mixer.music.load(music_files[current_index])
            pygame.mixer.music.play()
            song = os.path.basename(music_files[current_index])
            status.value = f"Now playing: {song}"
        except Exception as ex:
            status.value = f"Error: {ex}"
        try:
            generate_waveform(music_files[current_index], "waveform.png")
            waveform.src = "waveform.png?t=" + str(time.time())
        except Exception as ex:
            print(f"Waveform error: {ex}")
        page.update()
        threading.Thread(target=progress_update, daemon=True).start()

    def pause(_):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            status.value = "Paused"
            page.update()

    def stop(_):
        pygame.mixer.music.stop()
        status.value = "Stopped"
        progress.value = 0
        page.update()

    def next_song(_):
        nonlocal current_index
        if not music_files:
            return
        if shuffle:
            current_index = random.randint(0, len(music_files)-1)
        else:
            current_index = (current_index + 1) % len(music_files)
        play(None)

    def prev_song(_):
        nonlocal current_index
        if not music_files:
            return
        current_index = (current_index - 1) % len(music_files)
        play(None)

    def toggle_repeat(_):
        nonlocal repeat
        repeat = not repeat
        repeat_btn.text = f"Repeat: {'On' if repeat else 'Off'}"
        page.update()

    def toggle_shuffle(_):
        nonlocal shuffle
        shuffle = not shuffle
        shuffle_btn.text = f"Shuffle: {'On' if shuffle else 'Off'}"
        page.update()

    def progress_update():
        while pygame.mixer.music.get_busy():
            try:
                audio = MP3(music_files[current_index])
                length = audio.info.length
                elapsed = pygame.mixer.music.get_pos() / 1000
                progress.value = elapsed / length
                page.update()
                time.sleep(0.1)
            except:
                break
        if repeat:
            play(None)
        elif shuffle:
            next_song(None)

    status = ft.Text("No song playing", size=16, color="blue")
    progress = ft.ProgressBar(width=400, value=0, color="blue")
    waveform = ft.Image(src="", width=400, height=100)
    file_picker = ft.FilePicker(on_result=add_files)
    page.overlay.append(file_picker)

    add_btn = ft.ElevatedButton("Add Music", icon=ft.icons.ADD, on_click=lambda _: file_picker.pick_files(allow_multiple=True))
    play_btn = ft.ElevatedButton("Play", icon=ft.icons.PLAY_CIRCLE, on_click=play)
    pause_btn = ft.ElevatedButton("Pause", icon=ft.icons.PAUSE_CIRCLE, on_click=pause)
    stop_btn = ft.ElevatedButton("Stop", icon=ft.icons.STOP_CIRCLE, on_click=stop)
    next_btn = ft.ElevatedButton("Next", icon=ft.icons.SKIP_NEXT, on_click=next_song)
    prev_btn = ft.ElevatedButton("Previous", icon=ft.icons.SKIP_PREVIOUS, on_click=prev_song)
    repeat_btn = ft.ElevatedButton("Repeat: Off", icon=ft.icons.REPEAT, on_click=toggle_repeat)
    shuffle_btn = ft.ElevatedButton("Shuffle: Off", icon=ft.icons.SHUFFLE, on_click=toggle_shuffle)

    playlist = ft.Column(scroll="auto", expand=True, spacing=10, height=300)

    controls = ft.Column([
        ft.Row([prev_btn, play_btn, pause_btn, stop_btn, next_btn], alignment="center"),
        ft.Divider(),
        ft.Row([repeat_btn, shuffle_btn], alignment="center"),
        ft.Divider(),
        progress,
        status,
        waveform,
    ], scroll="auto", spacing=10)

    page.title = "CLOUD99 Music Player"
    page.theme_mode = "light"
    page.padding = 20
    page.scroll = "auto"

    page.add(
        ft.Column([
            ft.Row([
                ft.Text("CLOUD99 🎧 STUDIO", size=15, weight="bold"),
                ft.Text("🎼", size=20, weight="bold"),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(),
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([add_btn], alignment="center"),
                        ft.Divider(),
                    ]),
                    padding=10,
                    bgcolor=ft.colors.BLUE_GREY_50,
                    border_radius=10,
                )
            ),
            ft.Card(
                content=ft.Container(
                    content=controls,
                    padding=10,
                    bgcolor=ft.colors.BLUE_GREY_50,
                    border_radius=10,
                )
            ),
            ft.Container(
                content=playlist,
                padding=10,
                bgcolor=ft.colors.BLUE_GREY_100,
                border_radius=10,
            ),
            ft.Row([
                ft.Text("cloud99 studio v1.0", size=12, color=ft.colors.GREY_600),
                ft.Text("© 2023 cloud99 studio", size=12, color=ft.colors.GREY_600),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ], scroll="auto", expand=True, spacing=20)
    )

    pygame.mixer.init()

ft.app(target=main)
