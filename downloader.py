import logging
import os
import subprocess
from youtube_api import get_channel_name, get_song_name
from youtube_api import get_playlists, get_playlist_items
from song_utils import clean_for_file_path, clean_song_youtube_name, parse_youtube_title, tag_song

def download_channel(channel_id, api_key, mp3_tagging=True, download_location='C:\\Music'):

    # Get name of channel for file path, and clean up name.
	channel_name = get_channel_name(channel_id, api_key)
	channel_name = clean_for_file_path(channel_name)
	channel_file_path = os.path.join(download_location, channel_name)

	playlists = get_playlists(channel_id, api_key)

	for playlist_name, playlist_id in playlists:

		playlist_name = clean_for_file_path(playlist_name)
		
		print playlist_name, playlist_id

		download_playlist(playlist_id, playlist_name, api_key, mp3_tagging, channel_file_path)


def download_playlist(playlist_id, playlist_name, api_key, mp3_tagging=True, download_location='C:\\Music'):

	playlist_download_location = download_location

	if playlist_name is not None:
		playlist_name = clean_for_file_path(playlist_name)
		playlist_download_location = os.path.join(download_location, playlist_name)

	playlist_items = get_playlist_items(playlist_id, api_key)

	for song_name, song_id in playlist_items:

		download_song(song_id, api_key, mp3_tagging, download_location=playlist_download_location)

def download_song(song_id, api_key, mp3_tagging=True, download_location='C:\\Music'):

	song_name = get_song_name(song_id, api_key)
	song_name = clean_song_youtube_name(song_name)

	yt_dl_output_path = os.path.join(download_location, song_name) + '.%(ext)s'
	song_file_path = os.path.join(download_location, song_name) + '.mp3'

	song_youtube_url = 'https://www.youtube.com/watch?v={}'.format(song_id)

	execution_arguments = ['youtube-dl', song_youtube_url, '-x', '--audio-format', 'mp3', 
							   '-o', yt_dl_output_path]

	return_status = subprocess.call(execution_arguments)


	if return_status != 0:
		logging.error('Downloading of song failed.')
		return
	
	# Try to tag the song
	song_author, song_title = parse_youtube_title(song_name)

	if mp3_tagging:
		tag_song(song_file_path, song_author, song_title)
	else:
		logging.info('Not tagging mp3s, set by user.')