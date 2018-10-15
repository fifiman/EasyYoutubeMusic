import logging
import requests

from utils import pretty_print_json

def form_get_request_playlist(channel_id, api_key, page_token='', max_results='50'):

	get_request = 'https://www.googleapis.com/youtube/v3/playlists/?maxResults={}&channelId={}&part=snippet%2CcontentDetails&key={}'.format(max_results, channel_id, api_key)

	if page_token:
		get_request += '&pageToken={}'.format(page_token)

	return get_request

def form_get_request_playlistitems(playlist_id, api_key, page_token='', max_results='50'):

	get_request = 'https://www.googleapis.com/youtube/v3/playlistItems/?maxResults={}&playlistId={}&part=snippet%2CcontentDetails&key={}'.format(max_results, playlist_id, api_key)

	if page_token:
		get_request += '&pageToken={}'.format(page_token)

	return get_request

def get_playlists(channel_id, api_key):

	has_next_page_token = True
	next_page_token = ''
	results = []

	while has_next_page_token:

		get_request = form_get_request_playlist(channel_id, api_key, page_token=next_page_token)

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

	has_next_page_token = True
	next_page_token = ''
	results = []

	while has_next_page_token:

		get_request = form_get_request_playlistitems(playlist_id, api_key, page_token=next_page_token)

		r = requests.get(get_request)

		if r.status_code == 200:
			logging.info('GET request succeeded for fetching playlist items.')

			json_response = r.json()
			# pretty_print_json(json_response)
			
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