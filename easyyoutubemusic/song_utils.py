import eyed3
import logging
import re
from unidecode import unidecode


def clean_song_youtube_name(song_name):
	"""
	Clean youtube song names so they can be valid paths and remove unnecessary text.

	Rules songs are cleaned by:
		1. Illegal characters for file paths are removed.
		2. Non-ASCII unicode characters are replaced with their ascii equivalent or most similiar.
		3. Anything between paranthesis or square brackets is removed, including the brackets themselves.
		4. Everything after the second dash, if exists, is removed.
		5. Compress consecutive spaces into one space.
	"""

	# 1. Remove illegal characters.
	illegal_chars = '<>:"/\\|?*'

	for char in illegal_chars:
		song_name = song_name.replace(char, '')

	# 2. Sub unicode characters to ascii types characters.
	song_name = unidecode(song_name)
	
	# 3. Remove anything inside of round or square brackets.
	song_name = re.sub(r'\([^()]*\)', '', song_name)
	song_name = re.sub(r'\[[^\[\]]*\]', '', song_name)

	# 4. Remove everything after second dash, if it exists.
	first_dash_index = song_name.find('-')

	if first_dash_index != -1:
		second_dash_index = song_name.find('-', first_dash_index+1)

		if second_dash_index != -1:
			song_name = song_name[:second_dash_index]

	# 5. Compress consecutive spaces into single space after all filtering.
	song_name = " ".join(song_name.split())

	return song_name

def clean_for_file_path(youtube_name):
	"""
	Clean youtube names just to be a valid file path, additional
	aesthetic filtering is not applied.

	Rules songs are cleaned by for file path.
		1. Illegal characters for file paths are removed.
		2. Non-ASCII unicode characters are replaced with their ascii equivalent or most similiar.
	"""

	# 1. Remove illegal characters
	illegal_chars = '<>:"/\\|?*'

	for char in illegal_chars:
		youtube_name = youtube_name.replace(char, '')

	# 2. Sub unicode characters to ascii types characters
	youtube_name = unicode(unidecode(youtube_name), encoding = "utf-8")

	return youtube_name

def parse_youtube_title(full_title):
	"""
	Parse song tags from youtube title.

	Current logic is to assumme the youtube title is always in format 'author-song title'.
	If there exists dashes in the title, up to the first dash is the author and the rest is the song title.
	If there are no dashes, return original title as song title.

	There will never be more than one dash because of the way we clean youtube titles.
	
	Return tuple (author_title, song_title)
	"""

	assert full_title.count('-') <= 1

	first_dash_index = full_title.find('-')

	if first_dash_index == -1:  # No dashes exist
		return (None, full_title)
	else:
		author = full_title[:first_dash_index].strip()
		song_title = full_title[first_dash_index + 1:].strip()

		return (author, song_title)


def tag_song(song_file_path, song_artist, song_title):
	"""
	Tag song given the song's artist and title.
	"""
	audiofile = eyed3.load(song_file_path)

	if audiofile is not None:
		if song_artist is not None:
			audiofile.tag.artist = song_artist
		if song_title is not None:
			audiofile.tag.title = song_title

		audiofile.tag.save(song_file_path)

		logging.info("Successfully tagged file {} with tags artist={} and title={}.".format(
					 song_file_path, song_artist, song_title))
	else:
		logging.warning("Tagging failed for file {}.".format(song_file_path))