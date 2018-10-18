import os
from youtube_api import get_channel_name, get_playlists, get_playlist_items


def download_channel(channel_id, api_key, download_location='C:\Music'):

	channel_name = get_channel_name(channel_id, api_key)

	playlists = []#get_playlists(channel_id, api_key)

	for playlist_name, playlist_id in playlists:

		playlist_name = clean_song_youtube_name(playlist_name)
		playlist_download_location = os.path.join(download_location, playlist_name)
		
		print playlist_name, playlist_id, playlist_download_location





