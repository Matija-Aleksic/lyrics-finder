import os
import requests
import mutagen
import pyperclip
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
from bs4 import BeautifulSoup
import music_tag
import tkinter as tk
from tkinter import filedialog, simpledialog

# Function to get metadata from audio files
def get_metadata(filepath):
    try:
        _, ext = os.path.splitext(filepath)
        if ext in [".mp3", ".flac", ".ogg"]:
            audio = EasyID3(filepath) if ext == ".mp3" else FLAC(filepath) if ext == ".flac" else OggVorbis(filepath)
            artist = audio.get("artist", [""])[0]
            title = audio.get("title", [""])[0]
            return {"artist": artist, "title": title}
        else:
            # unsupported file format
            return None
    except NotImplementedError as e:
        print(f"Error processing file: {filepath}")
        print(f"Error details: {e}")
        return None

# Function to get lyrics from Genius
def get_lyrics(artist, title):
    base_url = "https://api.genius.com"
    search_url = "/search"
    headers = {"Authorization": "Bearer IZH7cNut75QpRsXf9Pyqnf-WBSCDmJKldwQjfvzLifboY6mIVRnBMiQIeJs21vQ6"}

    query = f"{artist} {title}"
    params = {"q": query}

    try:
        response = requests.get(base_url + search_url, params=params, headers=headers)
        response.raise_for_status()
        results = response.json()["response"]["hits"]

        if results:
            song_url = results[0]["result"]["url"]
            print("Genius URL:", song_url)

            # Fetch lyrics from the Genius website
            lyrics_response = requests.get(song_url)
            lyrics_response.raise_for_status()

            # Use BeautifulSoup to extract lyrics from HTML
            soup = BeautifulSoup(lyrics_response.text, "html.parser")
            lyrics = soup.find("div", class_="Lyrics__Container-sc-1ynbvzw-1 kUgSbL").get_text()

            print("Lyrics found:")
            print(lyrics)

            # Format lyrics
            formatted_lyrics = lyrics.replace('[', '\n[').replace(']', ']\n')
            return formatted_lyrics.strip()

    except requests.exceptions.RequestException as err:
        print("Something went wrong:", err)

    return None

# Function to delete lyrics from audio files
def delete_lyrics(filepath):
    try:
        f = music_tag.load_file(filepath)
        del f['lyrics']
        f.remove_tag('lyrics')
        f.save()
        print("Lyrics deleted successfully.")
    except Exception as e:
        print(f"Error deleting lyrics: {e}")

# Function for custom dialog box
def custom_dialog(title, prompt, buttons):
    root = tk.Tk()
    root.withdraw()

    result = simpledialog.askstring(title, prompt, buttons=buttons)

    return result

# Function to scan a folder and perform specified action
def scan_folder(folder_path, action_choice):
    for dirpath, _, filenames in os.walk(folder_path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            metadata = get_metadata(filepath)

            if metadata:
                print(metadata)
                artist = metadata["artist"]
                title = metadata["title"]

                if action_choice == "Find Lyrics":
                    lyrics = get_lyrics(artist, title)
                    if lyrics:
                        f = music_tag.load_file(filepath)
                        f['lyrics'] = lyrics
                        f.save()
                        print(lyrics)
                        pyperclip.copy(lyrics)
                    else:
                        print("Lyrics not found.")
                elif action_choice == "Delete Lyrics":
                    delete_lyrics(filepath)
                else:
                    print("Invalid choice.")

# Main script
buttons = ["Find Lyrics", "Delete Lyrics"]
answer = custom_dialog("Lyrics Action", "Do you want to find or delete lyrics for all songs in the folder?", buttons)

if answer:
    root = tk.Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory()

    # Call the function to scan the folder with the chosen action
    scan_folder(folder_path, answer)
else:
    print("Invalid choice.")
