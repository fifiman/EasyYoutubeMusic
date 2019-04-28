import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

import click

from easyyoutubemusic.downloader import (download_channel, download_playlist,
                                         download_song)
from easyyoutubemusic.youtube_api import parse_youtube_link


__author__ = "Nenad Bauk"


@click.command()
@click.argument('youtube_link')
@click.option('--enable-tagging/--disable-tagging', default=True, help='Enable/Disable mp3 tagging.')
@click.option('--output-path', type=click.Path(writable=True), help='Path to where music will be downloaded.')
@click.option('--api-key', help='Api key for Youtube API.')
def main(youtube_link, enable_tagging, output_path, api_key):
    """
Simple CLI for querying books on Google Books by Oyetoke Toby

Arguments:

    YOUTUBE_LINK : Link to youtube song, playlist, or channel to download. 
    """
    
    if output_path is None:
    	output_path = os.getcwd()

    download_link(youtube_link, output_path, api_key=None, enable_tagging=enable_tagging)

def load_api_key():
    key_dir = os.path.split(os.path.realpath(__file__))[0]
    key_path = os.path.join(key_dir, 'key.txt')

    with open(key_path) as f_key:
        key = f_key.read().strip()
        return key
    
    return None

def download_link(youtube_link, output_path, api_key=None, enable_tagging=True):
    # Try loading api key from file.
    api_key = load_api_key()

    if api_key is None:
        raise Exception('No api key available.')

    parsed_youtube_link = parse_youtube_link(youtube_link)

    if parsed_youtube_link is None:
        raise Exception('Passed argument is not a url to a song, playlist, or channel. Try again with a valid link.')

    link_type, link_id = parsed_youtube_link

    if link_type == 'song':
        download_song(link_id, api_key, enable_tagging, download_location=output_path)
    elif link_type == 'playlist':
        download_playlist(link_id, None, api_key, enable_tagging, download_location=output_path)
    elif link_type == 'channel':
        download_channel(link_id, api_key, enable_tagging, download_location=output_path)
    else:
        raise Exception('Youtube link is invalid. Please pass in the link to a video, playlist, or channel.')

if __name__ == "__main__":
    main()
