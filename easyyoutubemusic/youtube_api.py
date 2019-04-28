import logging
import re

import requests

from easyyoutubemusic.utils import pretty_print_json


def form_get_request_list_playlist(channel_id, api_key, page_token='', max_results='50'):
	"""
	Form get request to list all playlist of a certain channel.
	"""
	get_request = 'https://www.googleapis.com/youtube/v3/playlists/?maxResults={}&channelId={}&part=snippet%2CcontentDetails&key={}'.format(max_results, channel_id, api_key)

	if page_token:
		get_request += '&pageToken={}'.format(page_token)

	return get_request

def form_get_request_list_playlistitems(playlist_id, api_key, page_token='', max_results='50'):
	"""
	Form get request to list all playlist items of a certain playlist.
	"""
	get_request = 'https://www.googleapis.com/youtube/v3/playlistItems/?maxResults={}&playlistId={}&part=snippet%2CcontentDetails&key={}'.format(max_results, playlist_id, api_key)

	if page_token:
		get_request += '&pageToken={}'.format(page_token)

	return get_request

def get_playlists(channel_id, api_key):
	"""
	Fetch all playlists for a certain channel.

	This might take multiple get requests if there are many playlists. This is why
	next page tokens are to be passed from one get request to the next, until all
	playlists are exhausted.

	Returns list of playlists in tuple form (playlist_title, playlist_id).
	"""
	has_next_page_token = True
	next_page_token = ''
	results = []

	while has_next_page_token:

		get_request = form_get_request_list_playlist(channel_id, api_key, page_token=next_page_token)

		r = requests.get(get_request)

		if r.status_code == 200:
			logging.info('GET request succeeded for fetching playlists.')

			json_response = r.json()

			for playlist in json_response["items"]:
				results.append((playlist['snippet']['title'], playlist['id']))

			# Might not have fetched all playlists.
			if 'nextPageToken' in json_response:
				has_next_page_token = True
				next_page_token = json_response['nextPageToken']
			else:
				has_next_page_token = False
		else:
			logging.info('GET request failed for fetching playlists. Status code: {}, response: {}'.format(r.status_code, r.text))
			break

	return results

def get_playlist_items(playlist_id, api_key):
	"""
	Fetch all videos for a certain playlist.

	This might take multiple get requests if there are many videos. This is why
	next page tokens are to be passed from one get request to the next, until all
	videos are exhausted.

	Returns list of videos in tuple form (video_title, video_id).
	"""
	has_next_page_token = True
	next_page_token = ''
	results = []

	while has_next_page_token:

		get_request = form_get_request_list_playlistitems(playlist_id, api_key, page_token=next_page_token)

		r = requests.get(get_request)

		if r.status_code == 200:
			logging.info('GET request succeeded for fetching playlist items.')

			json_response = r.json()
			
			for song in json_response["items"]:
				results.append((song['snippet']['title'], song['snippet']['resourceId']['videoId']))

			# Might not have fetched all playlists.
			if 'nextPageToken' in json_response:
				has_next_page_token = True
				next_page_token = json_response['nextPageToken']
			else:
				has_next_page_token = False
			
			break
		else:
			logging.info('GET request failed for fetching playlist items. Status code: {}, response: {}'.format(r.status_code, r.text))
			break

	return results


def get_channel_name(channel_id, api_key):
	"""
	Fetch channel name through it's channel id.
	"""
	get_request = 'https://www.googleapis.com/youtube/v3/channels?id={}&part=snippet&key={}'.format(channel_id, api_key)

	r = requests.get(get_request)

	if r.status_code == 200:
		logging.info('GET request succeeded for fetching channel name.')

		json_response = r.json()
		return json_response['items'][0]['snippet']['title']		
	else:
		logging.info('GET request failed for fetching channel name. Status code: {}, response: {}'.format(r.status_code, r.text))
		return None

def get_song_name(video_id, api_key):
	"""
	Fetch video name through it's video id.
	"""
	get_request = 'https://www.googleapis.com/youtube/v3/videos?id={}&part=snippet&key={}'.format(video_id, api_key)

	r = requests.get(get_request)

	if r.status_code == 200:
		logging.info('GET request succeeded for song name.')

		json_response = r.json()
		return json_response['items'][0]['snippet']['title']		
	else:
		logging.info('GET request failed for fetching song name. Status code: {}, response: {}'.format(r.status_code, r.text))
		return None


def parse_youtube_link(youtube_url):
	"""
	Determine whether link is for song, playlist, or channel.

	Supported url formats:
	 - Videos:		https://www.youtube.com/watch?v={VIDEO_ID}
	 - Playlist:	https://www.youtube.com/playlist?list={PLAYLIST_ID}
	 - Channel:		https://www.youtube.com/channel/{CHANNEL_ID}

	Return tuple in the form (url_type, url_id).
	"""

	# youtube_song_regex = r'.*(?:youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=)([^#\&\?]*).*'
	youtube_song_regex = r'https://www\.youtube\.com\/watch\?v=([^#\&\?]*).*'	
	song_match = re.match(youtube_song_regex, youtube_url)

	youtube_playlist_regex = r'https://www\.youtube\.com/playlist\?list=([^#\&\?]*).*'
	playlist_match = re.match(youtube_playlist_regex, youtube_url)

	youtube_channel_regex = r'https://www\.youtube\.com/channel\/([^#\&\?]*).*'
	channel_match = re.match(youtube_channel_regex, youtube_url)

	if song_match is not None:
		return ('song', song_match.group(1))
	elif playlist_match is not None:
		return ('playlist', playlist_match.group(1))
	elif channel_match is not None:
		return ('channel', channel_match.group(1))
	else:
		return None
