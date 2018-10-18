import click
import os
from downloader import download_channel, download_playlist, download_song
from youtube_api import parse_youtube_link

__author__ = "Nenad Bauk"

youtube_api_key = 'AIzaSyD7LTx-ECbBMewfjX6dzgnxDL7HxLTRZvY'
my_channel_id = 'UCxEFrjBmbt2CLCFaAtGxaRA'


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

    if api_key is None:
    	api_key = youtube_api_key

    parsed_youtube_link = parse_youtube_link(youtube_link)

    if parsed_youtube_link is None:
        print 'Passed argument is not a url to a song, playlist, or channel. Try again with a valid link.'
        return

    link_type, link_id = parsed_youtube_link

    if link_type == 'song':
        download_song(link_id, api_key, enable_tagging, download_location=output_path)
    elif link_type == 'playlist':
    	# No playlist name specified
        download_playlist(link_id, None, api_key, enable_tagging, download_location=output_path)
    elif link_type == 'channel':
        download_channel(link_id, api_key, enable_tagging, download_location=output_path)
    else:
        print 'error'
        return

if __name__ == "__main__":
    main()