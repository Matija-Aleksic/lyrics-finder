
# Music Lyrics Finder

This Python script allows you to scan a folder of music files, retrieve song lyrics from Genius API, and update the lyrics metadata in the corresponding audio files. It supports popular audio formats like MP3 and FLAC. The script allows you to choose whether to delete existing lyrics or add new ones based on the available metadata.

## Features

- Extract metadata (artist, title, and lyrics) from audio files (MP3 and FLAC).
- Fetch lyrics from the Genius API.
- Delete old lyrics and replace them with new ones (optional).
- A simple graphical interface to choose actions (delete existing lyrics or add new ones).
- Supports adding and removing lyrics in both MP3 and FLAC files.
- Now with a simple webapp interface!

## Requirements

- Python 3.6 or higher
- Required Python libraries:
  - `requests`
  - `music-tag`
  - `mutagen`
  - `beautifulsoup4`
  - `pyperclip`
  - `eyed3`
  - `python-dotenv`
  - `tkinter`

You can install the necessary libraries with the following command:

```bash
pip install requests music-tag mutagen beautifulsoup4 pyperclip eyed3 python-dotenv flask
```


## Setting up the Genius API Key

Before running the script, you need to set up your Genius API key as an environment variable.

### Linux/macOS

To set the `GENIUS_API_KEY` variable in Linux or macOS, open a terminal and run the following command:

```bash
export GENIUS_API_KEY="your_genius_api_key"
```

### Windows

On Windows, you can set the `GENIUS_API_KEY` variable using the Command Prompt or PowerShell.

**Using Command Prompt:**

```cmd
set GENIUS_API_KEY=your_genius_api_key
```

**Using PowerShell:**

```powershell
$env:GENIUS_API_KEY="your_genius_api_key"
```

## Usage

1. **Open the web interface:** After running the program, Ctrl + click on the provided ip address on the CMD.
2. **Select a folder:** Using the browse button select the folder containing the music files you want to process (note that for now this only works for folders located in the same parent directory as the .py program).
3. **Delete Old Lyrics:** Using the radial menu select if you want to delete old lyrics before adding new ones.
   - **Yes:** Deletes old lyrics and adds new lyrics fetched from Genius.
   - **No:** Keeps existing lyrics and only adds new ones if they don't already exist.
4. The script will scan the folder recursively and process all files.
