from flask import Flask, render_template, url_for, request, jsonify
import os
from lyric_finder_utilities import get_metadata, get_lyrics, add_lyrics, delete_lyric

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_folder', methods=['POST'])
def process_folder():
    folder_path = request.json.get("folder_path")
    delete_old = request.json.get("delete_old")
    
    if not folder_path or not action_choice:
        return {"error": "Missing folder path or action choice"}, 400

    try:
        scan_folder(folder_path, action_choice)
        return {"status": "success"}
    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}, 500

    for dirpath, _, filenames in os.walk(folder_path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            metadata = get_metadata(filepath)
            if metadata:
                artist, title = metadata["artist"], metadata["title"]
                if delete_old:
                    delete_lyrics(filepath)
                lyrics = get_lyrics(artist, title)
                if lyrics:
                    add_lyrics(filepath, lyrics)
    
    return jsonify({"message": "Processing complete"})

if __name__ == "__main__":
    app.run(debug=True)