import logging
import os
import subprocess

from easyyoutubemusic.song_utils import (clean_for_file_path,
                                         clean_song_youtube_name,
                                         parse_youtube_title, tag_song)
from easyyoutubemusic.youtube_api import (get_channel_name, get_playlist_items,
                                          get_playlists, get_song_name)


def download_channel(channel_id, api_key, overwrite, mp3_tagging=True, download_location='C:\\Music'):
	"""
	Download all playlists of a given channel.

	Channel name is fetched to be appended to the download location file path,
	and all of the channel's playlists will be downloaded to this new path.

	Returns:
		None
	"""

    # Get name of channel for file path, and clean up name.
	channel_name = get_channel_name(channel_id, api_key)
	channel_name = clean_for_file_path(channel_name)
	channel_file_path = os.path.join(download_location, channel_name)

	playlists = get_playlists(channel_id, api_key)

	for playlist_name, playlist_id in playlists:

		playlist_name = clean_for_file_path(playlist_name)
		
		print(playlist_name, playlist_id)

		download_playlist(playlist_id, playlist_name, api_key, overwrite, mp3_tagging, channel_file_path)


def download_playlist(playlist_id, playlist_name, api_key, overwrite, mp3_tagging=True, download_location='C:\\Music'):
	"""
	Download all videos of a given playlist.
	
	Playlist name cannot be fetched through the Youtube API. Therefore, if a
	playlist name is given it will be appended to the download location file
	path. Otherwise it will remain unchanged.

	Returns:
		None
	"""
	playlist_download_location = download_location

	if playlist_name is not None:
		playlist_name = clean_for_file_path(playlist_name)
		playlist_download_location = os.path.join(download_location, playlist_name)

	playlist_items = get_playlist_items(playlist_id, api_key)

	for song_name, song_id in playlist_items:

		download_song(song_id, api_key, overwrite, mp3_tagging, download_location=playlist_download_location)

def download_song(video_id, api_key, overwrite, mp3_tagging=True, download_location='C:\\Music'):
	"""
	Download given video and convert to mp3 format in the given location.

	Optionally, the downloaded mp3 can be given ID3 tags based on the video's title. 	

	Returns:
		None
	"""
	song_name = get_song_name(video_id, api_key)
	song_name = clean_song_youtube_name(song_name)

	yt_dl_output_path = os.path.join(download_location, song_name) + '.%(ext)s'
	song_file_path = os.path.join(download_location, song_name) + '.mp3'

	if overwrite or not os.path.isfile(song_file_path):
		song_youtube_url = 'https://www.youtube.com/watch?v={}'.format(video_id)
		execution_arguments = ['youtube-dl', song_youtube_url, '-x', '--audio-format', 'mp3', '-o', yt_dl_output_path]
		return_status = subprocess.call(execution_arguments)

		if return_status != 0:
			logging.error('Downloading of video failed. Video id: {}.'.format(video_id))
			return
	
	if mp3_tagging:
		song_author, song_title = parse_youtube_title(song_name)
		logging.info("Tagging song {} with author {} and title {}.".format(song_name, song_author, song_title))
		tag_song(song_file_path, song_author, song_title)
