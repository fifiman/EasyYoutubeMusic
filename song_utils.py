import eyed3
import re
from unidecode import unidecode


def clean_song_youtube_name(song_name):

	# Remove illegal characters
	illegal_chars = '<>:"/\\|?*'

	for char in illegal_chars:
		song_name = song_name.replace(char, '')

	# Sub unicode characters to ascii types characters
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

	if song_artist is not None:
		audiofile.tag.artist = song_artist
	if song_title is not None:
		audiofile.tag.title = song_title

	audiofile.tag.save(song_file_path)
