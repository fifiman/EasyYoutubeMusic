# About
EasyYoutubeMusic is a Python command-line tool for downloading your music from YouTube. It downloads the video's audio through `youtube-dl` and adds mp3 tags with `eyeD3`.

For example, here is how you would download a song to your music folder `C:\Music`:

`python main.py https://www.youtube.com/watch?v=XEjLoHdbVeE --output-path="C:\Music" `


# Usage
Supported YouTube link types:
- Video `https://www.youtube.com/watch?v={VIDEO_ID}`
- Playlist `https://www.youtube.com/playlist?list={PLAYLIST_ID}`
- Channel `https://www.youtube.com/channel/{CHANNEL_ID}`


Use `python main.py --help` for help on all available features.

# Installation
Install the following packages:

`pip install youtube-dl`

`pip install eyeD3`

For audio conversion you will need to install ffmpeg. It is best to install chocolatey and run `choco install ffmpeg`.

# MP3 Tagging
The current logic for tagging mp3s assumes that the YouTube title for songs is in format `Artist - Song Title`. If there are no dashes, artist will be left empty and the entire YouTube title will be the song title. 
