import errno
import eyed3
import logging
import os
import re
import requests
import subprocess
from song_utils import clean_song_youtube_name, parse_youtube_title, tag_song
from youtube_api import get_playlists, get_playlist_items


channel_id = 'UCxEFrjBmbt2CLCFaAtGxaRA'
api_key = 'AIzaSyD7LTx-ECbBMewfjX6dzgnxDL7HxLTRZvY'
music_download_location = 'C:\Music'


if __name__ == '__main__':

	playlists = get_playlists(channel_id, api_key)

	for playlist_name, playlist_id in playlists:

		playlist_name = clean_song_youtube_name(playlist_name)

		print playlist_name, playlist_id

		playlist_folder_path = os.path.join(music_download_location, playlist_name)

		playlist_songs = get_playlist_items(playlist_id, api_key)

		for song_name, song_id in playlist_songs:
			# Filters to ensure youtube title does not contain bad characters
			song_name = clean_song_youtube_name(song_name)

			song_path = os.path.join(playlist_folder_path, song_name) + '.%(ext)s'
			song_file_path = os.path.join(playlist_folder_path, song_name) + '.mp3'

			print song_name, song_file_path

			song_youtube_url = 'https://www.youtube.com/watch?v={}'.format(song_id)

			execution_arguments = ['youtube-dl', song_youtube_url, '-x', '--audio-format', 'mp3', 
								   '-o', song_path]
			
			return_status = subprocess.call(execution_arguments)


			if return_status != 0:
				logging.error('Downloading of song failed.')
				continue
			
			# Try to tag the song
			song_author, song_title = parse_youtube_title(song_name)
			tag_song(song_file_path, song_author, song_title)
		