
import click
from downloader import download_channel
from youtube_api import parse_youtube_link

__author__ = "Nenad Bauk"

youtube_api_key = 'AIzaSyD7LTx-ECbBMewfjX6dzgnxDL7HxLTRZvY'
my_channel_id = 'UCxEFrjBmbt2CLCFaAtGxaRA'


@click.command()
@click.argument('youtube_link')
def main(youtube_link):
    """
Simple CLI for querying books on Google Books by Oyetoke Toby

Arguments:

    YOUTUBE_LINK : Link to youtube song, playlist, or channel to download. 
    """

    parsed_youtube_link = parse_youtube_link(youtube_link)

    if parsed_youtube_link is None:
        print 'Passed argument is not a url to a song, playlist, or channel. Try again with a valid link.'
        return

    link_type, link_id = parsed_youtube_link

    if link_type == 'song':
        print 'Cant handle songs yet'
    elif link_type == 'playlist':
        print 'Cant handle playlists yet'
    elif link_type == 'channel':
        download_channel(link_id, youtube_api_key)
    else:
        print 'error'
        return

if __name__ == "__main__":
    main()