import os
import requests
import music_tag
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
from bs4 import BeautifulSoup
import pyperclip

def get_metadata(filepath):
    try:
        _, ext = os.path.splitext(filepath)
        if ext == ".mp3" or ext == ".flac" or ext == ".ogg":
            audio = EasyID3(filepath) if ext == ".mp3" else FLAC(filepath) if ext == ".flac" else OggVorbis(filepath)
            artist = audio.get("artist", [""])[0]
            title = audio.get("title", [""])[0]
            return {"artist": artist, "title": title}
        else:
            return None
    except NotImplementedError as e:
        print(f"Error processing file: {filepath}")
        print(f"Error details: {e}")
        return None

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

            lyrics_response = requests.get(song_url)
            lyrics_response.raise_for_status()
            
            soup = BeautifulSoup(lyrics_response.text, "html.parser")
            lyrics_container = soup.find("div", class_="Lyrics__Container-sc-1ynbvzw-1 kUgSbL")

            # Get the text content of the lyrics container
            lyrics_text = lyrics_container.get_text(separator='\n')

            print("Lyrics found:")
            print(lyrics_text)

            formatted_lyrics = lyrics_text.replace('[', '\n[')
            formatted_lyrics = formatted_lyrics.replace(']', ']\n')

            return formatted_lyrics.strip()


    except requests.exceptions.RequestException as err:
        print("Something went wrong:", err)

    return None

def delete_lyrics(filepath):
    try:
        f = music_tag.load_file(filepath)
        del f['lyrics']
        f.remove_tag('lyrics')
        f.save()
        print("Lyrics deleted successfully.")
    except Exception as e:
        print(f"Error deleting lyrics: {e}")

def custom_dialog_yes_no(title, prompt):
    root = tk.Tk()
    root.withdraw()

    result = messagebox.askyesno(title, prompt)

    return result

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

# Ask user whether to find or delete lyrics for the entire folder
answer = custom_dialog_yes_no("Lyrics Action", "Do you want to find the lyrics? (pressing no will delete them)")

if answer:
    root = tk.Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory()

    # Call the function to scan the folder with the chosen action
    action_choice = "Find Lyrics" if answer else "Delete Lyrics"
    scan_folder(folder_path, action_choice)
else:
    print("User chose not to proceed.")
