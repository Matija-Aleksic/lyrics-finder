import os
import requests
import music_tag
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC
from mutagen.id3 import ID3NoHeaderError
from bs4 import BeautifulSoup
import eyed3
import time
import random
from dotenv import load_dotenv
from base import insert_song, get_all_songs, create_table, search_songs

load_dotenv()
app = Flask(__name__)
app.secret_key = os.urandom(24)
CMDOutput = ""


create_table()


def get_metadata(filepath):
    global CMDOutput
    try:
        _, ext = os.path.splitext(filepath)
        if ext == ".mp3":
            audio = EasyID3(filepath)
            artist = audio.get("artist", [""])[0]
            title = audio.get("title", [""])[0]
            mp3_file = eyed3.load(filepath)

            if mp3_file and mp3_file.tag:
                uslt_frames = mp3_file.tag.frame_set.get(b'USLT')
                old_lyrics = [frame.text for frame in uslt_frames] if uslt_frames else None
            else:
                old_lyrics = None

        elif ext == ".flac":
            audio = FLAC(filepath)
            artist = audio.get("artist", [""])[0]
            title = audio.get("title", [""])[0]
            old_lyrics = audio.tags.get("LYRICS", [])
            old_lyrics = old_lyrics[0] if old_lyrics else None
        else:
            return None

        tags = {"artist": artist, "title": title, "old_lyrics": old_lyrics is not None}
        CMDOutput += f"{tags}\n"
        return tags

    except (ID3NoHeaderError, NotImplementedError) as e:
        print(f"Error processing file: {filepath}\nDetails: {e}")
        return None


def get_lyrics(artist, title):
    global CMDOutput
    GENIUS_API_KEY = os.getenv("GENIUS_API_KEY")
    if not GENIUS_API_KEY:
        raise ValueError("Genius API key not found. Set GENIUS_API_KEY environment variable.")

    base_url = "https://api.genius.com"
    headers = {"Authorization": f"Bearer {GENIUS_API_KEY}"}
    params = {"q": f"{artist} {title}"}

    try:
        response = requests.get(f"{base_url}/search", params=params, headers=headers)
        response.raise_for_status()
        results = response.json().get("response", {}).get("hits", [])

        if results:
            song_url = results[0]["result"]["url"]
            CMDOutput += f"Genius URL: {song_url}\n"

            time.sleep(random.uniform(0, 4))

            lyrics_response = requests.get(song_url)
            lyrics_response.raise_for_status()
            soup = BeautifulSoup(lyrics_response.text, "html.parser")
            lyrics_container = soup.find("div", class_="Lyrics-sc-1bcc94c6-1 bzTABU")

            if lyrics_container:
                lyrics_text = lyrics_container.get_text(separator='\n')
                CMDOutput += f"Lyrics found:\n{lyrics_text}\n\n"
                return lyrics_text.replace('[', '\n[').replace(']', ']\n').strip()

    except requests.exceptions.RequestException as err:
        print(f"Error fetching lyrics: {err}")
        CMDOutput += "Error fetching lyrics\n"

    return None


def delete_lyrics(filepath):
    global CMDOutput
    try:
        f = music_tag.load_file(filepath)
        del f['lyrics']
        f.remove_tag('lyrics')
        f.save()
        CMDOutput += "Lyrics deleted successfully\n"
    except Exception as e:
        CMDOutput += f"Error deleting lyrics: {e}\n"


def add_lyrics(filepath, lyrics):
    global CMDOutput
    try:
        f = music_tag.load_file(filepath)
        f['lyrics'] = lyrics
        f.save()
        CMDOutput += "Lyrics added successfully\n\n\n"
    except Exception as e:
        CMDOutput += f"Error adding lyrics: {e}\n"


def scan_folder(folder_path, action_choice):
    global CMDOutput
    for dirpath, _, filenames in os.walk(folder_path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            metadata = get_metadata(filepath)
            if metadata:
                artist = metadata["artist"]
                title = metadata["title"]
                old_lyrics = metadata.get("old_lyrics")

                if action_choice == "yes":
                    lyrics = get_lyrics(artist, title)
                    if lyrics:
                        insert_song(artist, title, lyrics)  
                        delete_lyrics(filepath)
                        add_lyrics(filepath, lyrics)
                    else:
                        CMDOutput += "New lyrics not found. Old lyrics preserved.\n"
                elif action_choice == "no":
                    if old_lyrics:
                        CMDOutput += "Old lyrics exist, skipping\n"
                    else:
                        lyrics = get_lyrics(artist, title)
                        if lyrics:
                            insert_song(artist, title, lyrics)  

                            add_lyrics(filepath, lyrics)
        
        display_songs_from_db()

def display_songs_from_db():
    print("Songs stored in database: ")
    songs = get_all_songs()
    for song in songs:
        print(f"Artist: {song[0]}, Title: {song[1]}")





@app.route('/')
def index():
    message = request.args.get('message', '')
    return render_template('index.html')


@app.route('/process_files', methods=['POST'])
def process_files():
    folder_name = request.form['folder_path']
    base_dir = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(base_dir, folder_name)

    if not os.path.exists(folder_path):
        return jsonify({"status": "error", "message": "Folder not found."}), 404

    action_choice = request.form['action_choice']
    scan_folder(folder_path, action_choice)

    flash('Files processed successfully!')

    return redirect(url_for('index', message="Files processed successfully."))


@app.route('/get_message', methods=['GET'])
def get_message():
    global CMDOutput
    CMDPackage = CMDOutput
    CMDOutput = ""
    return jsonify({"message": CMDPackage})


@app.route('/list_songs', methods=['GET'])
def list_songs():
    songs = get_all_songs()
    return jsonify([{"artist": song[0], "title": song[1], "lyrics": song[2]} for song in songs])



@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = request.form['query'].strip() 
        if query:  
            results = search_songs(query) 
            return render_template('search_results.html', songs=results, query=query)
        else:
            return render_template('search.html', message="Please enter a search query.") 
    return render_template('search.html')  





if __name__ == "__main__":
    app.run(debug=True)