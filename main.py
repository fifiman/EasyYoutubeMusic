import errno
import eyed3
import json
import logging
import os
import requests
import subprocess

import re

# logging.basicConfig(level=logging.DEBUG)

channel_id = 'UCxEFrjBmbt2CLCFaAtGxaRA'
max_results = '50'
api_key = 'AIzaSyD7LTx-ECbBMewfjX6dzgnxDL7HxLTRZvY'

get_request = "https://www.googleapis.com/youtube/v3/playlists/?maxResults={}&channelId={}&part=snippet%2CcontentDetails&key={}".format(max_results, channel_id, api_key)

def create_directory(dir_path):
	if not os.path.exists(os.path.dirname(dir_path)):
	    try:
	        os.makedirs(os.path.dirname(dir_path))
	    except OSError as exc: # Guard against race condition
	        if exc.errno != errno.EEXIST:
	            raise

def pretty_print_json(json_text):
	print(json.dumps(json_text, indent=2))

def clean_song_youtube_name(song_name):

	# Remove illegal characters
	illegal_chars = '<>:"/\\|?*'

	for char in illegal_chars:
		song_name = song_name.replace(char, '')

	# Sub unicode characters to ascii types characters
	from unidecode import unidecode
	song_name = unicode(unidecode(song_name), encoding = "utf-8")
	
	# Remove anything inside of round or square brackets
	song_name = re.sub(r'\([^()]*\)', '', song_name)
	song_name = re.sub(r'\[[^\[\]]*\]', '', song_name)

	# Remove everything after second dash, if it exists
	first_dash_index = song_name.find('-')

	if first_dash_index != -1:
		second_dash_index = song_name.find('-', first_dash_index+1)

		if second_dash_index != -1:
			song_name = song_name[:second_dash_index]

	# Remove unnecesary words
	filter_words = []


	#Remove consecutive spaces after all filtering
	song_name = " ".join(song_name.split())

	return song_name


def parse_youtube_title(full_title):
	'''
	Current logic is to assumme the youtube title is always in format 'author-song title'.
	If there exists dashes in the title, up to the first dash is the author and the rest is the song title.
	If there are no dashes, return original title as song title.
	
	Return tuple (author_title, song_title)
	'''

	first_dash_index = full_title.find('-')

	print first_dash_index

	if first_dash_index == -1:
		return (None, full_title)
	else:
		author = full_title[:first_dash_index].strip()
		song_title = full_title[first_dash_index + 1:].strip()

		return (author, song_title)


def tag_song(song_file_path, song_artist, song_title):

	audiofile = eyed3.load(song_file_path)

	if song_author is not None:
		audiofile.tag.artist = song_author
	if song_title is not None:
		audiofile.tag.title = song_title

	audiofile.tag.save(song_file_path)


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
			pretty_print_json(json_response)
			
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


if __name__ == '__main__':

	playlists = get_playlists(channel_id, api_key)

	music_download_location = 'C:\Music'


	for playlist_name, playlist_id in playlists:

		playlist_name = clean_song_youtube_name(playlist_name)

		print playlist_name, playlist_id

		playlist_folder_path = os.path.join(music_download_location, playlist_name)
		# create_directory(playlist_folder_path)

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
		