import logging
import re

import requests


# TODO: Add throttling for youtube API reque

class YoutubeApiException(Exception):
    "Expcetion for when we fail to deal with response from the Youtube API."
    pass


def form_get_request_to_list_playlists_of_channel(channel_id, api_key, page_token='', max_results='50'):
    """
	Form get request to list all playlist of a certain channel.
	"""
    get_request = 'https://www.googleapis.com/youtube/v3/playlists/?maxResults={}&channelId={}&part=snippet%2CcontentDetails&key={}'.format(
        max_results, channel_id, api_key)

    if page_token:
        get_request += '&pageToken={}'.format(page_token)

    return get_request


def form_get_request_to_list_songs_of_playlist(playlist_id, api_key, page_token='', max_results='50'):
    """
	Form get request to list all playlist items of a certain playlist.
	"""
    get_request = 'https://www.googleapis.com/youtube/v3/playlistItems/?maxResults={}&playlistId={}&part=snippet%2CcontentDetails&key={}'.format(
        max_results, playlist_id, api_key)

    if page_token:
        get_request += '&pageToken={}'.format(page_token)

    return get_request


def get_playlists_of_channel(channel_id, api_key):
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
        get_request = form_get_request_to_list_playlists_of_channel(channel_id, api_key, page_token=next_page_token)
        logging.info(
            "Sending the following GET request for fetching playlists from channel. Request: {}".format(get_request))
        r = requests.get(get_request)

        if r.status_code == 200:
            logging.info('GET request succeeded for fetching playlists.')

            json_response = r.json()
            try:
                for playlist in json_response["items"]:
                    results.append((playlist['snippet']['title'], playlist['id']))
            except KeyError as e:
                raise YoutubeApiException(
                    {"message": "Failed to extract values from channel response", "response": json_response}) from e

            # Might not have fetched all playlists.
            if 'nextPageToken' in json_response:
                has_next_page_token = True
                next_page_token = json_response['nextPageToken']
            else:
                has_next_page_token = False
        else:
            raise YoutubeApiException(
                {"message": "GET request failed for fetching playlists",
                 "response": r.text,
                 "status_code": r.status_code})

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
        get_request = form_get_request_to_list_songs_of_playlist(playlist_id, api_key, page_token=next_page_token)
        logging.info(
            "Sending the following GET request for fetching songs from playlist. Request: {}".format(get_request))

        r = requests.get(get_request)

        if r.status_code == 200:
            logging.info('GET request succeeded for fetching playlist items.')

            json_response = r.json()

            try:
                for song in json_response["items"]:
                    results.append((song['snippet']['title'], song['snippet']['resourceId']['videoId']))
            except KeyError as e:
                raise YoutubeApiException(
                    {"message": "Failed to extract values from playlist response", "response": json_response}) from e

            # Might not have fetched all playlists.
            if 'nextPageToken' in json_response:
                has_next_page_token = True
                next_page_token = json_response['nextPageToken']
            else:
                has_next_page_token = False

            break
        else:
            raise YoutubeApiException(
                {"message": "GET request failed for songs from playlist",
                 "response": r.text,
                 "status_code": r.status_code})

    return results


def get_channel_name(channel_id, api_key):
    """Fetch channel name through it's channel id. """
    get_request = 'https://www.googleapis.com/youtube/v3/channels?id={}&part=snippet&key={}'.format(channel_id, api_key)
    logging.info("Sending the following GET request for fetching channel name. Request: {}".format(get_request))

    r = requests.get(get_request)

    if r.status_code == 200:
        logging.info('GET request succeeded for fetching channel name.')

        json_response = r.json()
        try:
            # TODO: Handle channel does not exist.
            return json_response['items'][0]['snippet']['title']
        except (IndexError, KeyError) as e:
            raise YoutubeApiException(
                {"message": "Failed to extract value from channel name response", "response": json_response}) from e
    else:
        raise YoutubeApiException(
            {"message": "GET request failed for fetching channel name",
             "response": r.text,
             "status_code": r.status_code})


def get_song_name(video_id, api_key):
    """Fetch video name through it's video id. """
    get_request = 'https://www.googleapis.com/youtube/v3/videos?id={}&part=snippet&key={}'.format(video_id, api_key)
    logging.info("Sending the following GET request for fetching song name. Request: {}".format(get_request))

    r = requests.get(get_request)

    if r.status_code == 200:
        logging.info('GET request succeeded for song name.')

        json_response = r.json()

        try:
            # TODO: Handle song does not exist.
            return json_response['items'][0]['snippet']['title']
        except (IndexError, KeyError) as e:
            raise YoutubeApiException(
                {"message": "Failed to extract value from song name response", "response": json_response}) from e
    else:
        raise YoutubeApiException(
            {"message": "GET request failed for fetching song name",
             "response": r.text,
             "status_code": r.status_code})


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
