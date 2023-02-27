import os
import requests
import mutagen
import re
import pyperclip
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
from bs4 import BeautifulSoup
from mutagen import File
from mutagen.flac import Picture
from mutagen.id3 import ID3, USLT
import music_tag


unfound = 0;
def get_metadata(filepath):
    """Extracts artist and song metadata from an audio file."""
    _, ext = os.path.splitext(filepath)
    if ext == ".mp3":
        audio = EasyID3(filepath)
        artist = audio.get("artist", [""])[0]
        title = audio.get("title", [""])[0]
    elif ext == ".flac":
        audio = FLAC(filepath)
        artist = audio.get("artist", [""])[0]
        title = audio.get("title", [""])[0]
    elif ext == ".ogg":
        audio = OggVorbis(filepath)
        artist = audio.get("artist", [""])[0]
        title = audio.get("title", [""])[0]
    else:
        # unsupported file format
        return None
    return {"artist": artist, "title": title}



def get_lyrics(artist, title):
    """Searches for lyrics on lyrics.com and returns the lyrics if found."""
    artist = artist.lower().replace(" ", "-")
    title = title.lower().replace(" ", "-")
    query = artist + " " + title + " lyrics"

    url = "https://www.google.com/search?q=" + query
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        lyrics_div = soup.find("div", {"jsname": "WbKHeb"})
        if lyrics_div:
            
            lyrics_text = lyrics_div.get_text(strip=True)
            lyrics_text = " ".join(lyrics_text.split())

            # Split the text into lines based on the separator '.,'
            lines = lyrics_text.split('.,')

            # Strip any whitespace from each line
            lines = [line.strip() for line in lines]

            # Add a newline before every word that starts with a capital letter
            new_lines = []
            for line in lines:
                new_line = ""
                for i in range(len(line)):
                    if i > 0 and line[i].isupper():
                        new_line += "\n"
                    new_line += line[i]
                new_lines.append(new_line)

            # Join the lines with newline characters
            formatted_lyrics = '\n'.join(new_lines)
            return formatted_lyrics
    return None




def scan_folder(folder_path):
    print("test")
    """Scans a folder and its subfolders for audio files, extracts metadata, and adds lyrics if found."""
    for dirpath, _, filenames in os.walk(folder_path):
        for filename in filenames:

            filepath = os.path.join(dirpath, filename)
            metadata = get_metadata(filepath)
            print("test2")
            if metadata:
                print(filepath)
                print(metadata)
                artist = metadata["artist"]
                title = metadata["title"]
                lyrics = get_lyrics(artist, title)
                if lyrics:
                    """dodat lyrics preko mp3tag"""
                    if filename.endswith(".mp3"):
                        filepath1 = os.path.join(dirpath, filename)
                        f = music_tag.load_file(filepath1)
                        f['lyrics']=lyrics
                        f.save()
                        #lyrics = lyrics.replace("\n", "\n\n")
                        #audio = mutagen.File(filepath)
                        #audio["UNSYNCEDLYRICS"] = lyrics
                        #audio.save()
                        # Use MP3Tag command line interface to add the lyrics to the music file
                        """os.system("Mp3tag.exe /s \"" + filepath + "\" /ifv2 /xl /add UNSYNCEDLYRICS=\"" + lyrics + "\"")"""
                
                    elif filename.endswith(".flac"):
                        filepath2 = os.path.join(dirpath, filename)
                        f = music_tag.load_file(filepath2)
                        f['lyrics']=lyrics
                        f.save()
                        #lyrics = lyrics.replace("\n", "\n\n")
                        ## Use Mutagen to add the lyrics to the FLAC file
                        #audio = mutagen.File(filepath)
                        #audio["UNSYNCEDLYRICS"] = lyrics
                        #audio.save()
                    print(lyrics)
                    pyperclip.copy(lyrics)
                else:
                    unfound=+1
                    print("Lyrics not found")


scan_folder(os.path.expanduser("D:\pjesmee\slayer"))
print(unfound)
