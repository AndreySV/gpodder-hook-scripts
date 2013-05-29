# Summary

This repository contains gPodder hook scripts which I use for myself. Please feel free to fork or use this repository for your own purpose.

## gPodder hooks infrastructure (recommended way)

### What are hooks in gPodder?

Hooks are python scripts loaded by gPodder at runtime. Each script must define a class named "gPodderHooks", otherwise it will be ignored.

### How to configure

You could copy or link the scripts in this repository to ~/.config/gpodder/hooks/ and everything should work fine.

For gPodder "tres" (3.x branch), you need to place them in $GPODDER_HOME/Hooks/ (where $GPODDER_HOME defaults to ~/gPodder/ if you have not set it manually)

### How to create my own hook script?

See example documentation at [hooks.py](http://repo.or.cz/w/gpodder.git/blob/HEAD:/doc/dev/examples/hooks.py).

In the "tres" branch, the example is in examples/hooks.py.

# Hooks list


## bittorrent

Automatically open .torrent files with a BitTorrent client.


## cmml_linux_outlaws

Hooks script to create a CMML file containing chapters for Linux Outlaws.

### Requirements

- BeautifulSoup - Beautiful Soup is a Python HTML/XML parser designed for quick turnaround projects like screen-scraping (http://www.crummy.com/software/BeautifulSoup/)

   
## cmml_radiotux_magazin

Hooks script to create a CMML file containing chapters for the RadioTux Monthly magazin.

### Requirements

- BeautifulSoup (http://www.crummy.com/software/BeautifulSoup/)


## enqueue_in_vlc

This hook shows a new feature of the gPodder "tres" branch - you can now add
items to the episode list context menu. Each item needs to have a label and
a callable that will take a list of selected episodes. This script shows you
how to implement a "Enqueue in VLC" context menu item using hooks.

## download_new_episodes

Autodownload new episodes only for selected podcast feeds

On posix systems 'zenity' is necessary. User will be asked 
after addition new feed should be downloaded new episodes of 
the feed automaticaly or not. 
 
On other systems new episodes will not be downloaded 
automaticaly by default. To switch autodownload feature no
user need open auto_download.sqlite database with any db-client
and change where necessary records.

### Requirements

- zenify on posix systems

## flv2mp4

This script will automatically wrap FLV files from YouTube into a MP4 format
container after download. It also includes a context menu item for already-
downloaded files. This requires the "ffmpeg" utility to be installed. It only
works for YouTube videos (e.g. fmt_id = 35). For fmt_id 35 on YouTube, this
allows playback of the resulting files on a PS3 (H.264 + AAC), which does not
work with the FLV container, but does work with the MP4 container. The change
is quick, because no re-encoding is done.


## mp3gain

adjusts mp3s so that they all have the same volume. Contrary to normalize_audio this hook don't decode and re-encode the audio. But this hook only supports mp3 files.

### Requirements

- mp3gain - MP3Gain analyzes and adjusts mp3 files so that they have the same volume. (http://mp3gain.sourceforge.net/)


## mp3split

Split mp3 files in ranges of 10 minutes when the files are copied to the device.

### Requirements

- mp3splt binary on the path (http://mp3splt.sourceforge.net/)


## normalize_audio

adjusts mp3s/oggs so that they all have the same volume. Contrary to mp3gain this hook decode and re-encode the audio and supports mp3 and ogg files.

### Requirements

- normalize-audio - Normalize is a tool for adjusting the volume of audio files to a standard level (http://normalize.nongnu.org)
- mpg123 - Fast console MPEG Audio Player and decoder library (http://www.mpg123.de/)
- vorbis-tools - several Ogg Vorbis tools (https://www.xiph.org/downloads/)


## rename_downloads

Rename downloaded episodes based on their episode title in the feed.  


## reset_etag

Resets the etag and last modified information for a podcast. This could be necessary if the server lies about the last modified state.
This will cause gPodder to reload (and re-parse) the feed every time 


## rm_ogg_coover_hook

This hook scripts removes coverart from all downloaded ogg files.
The reason for this script is that my media player (MEIZU SL6) could not handle ogg files with included coverart. 

### Requirements

- python-mutagen - Mutagen is a Python module to handle audio metadata. (http://code.google.com/p/mutagen/)


## rockbox_mp4_convert

This script converts any mp4 videos to play on a Sansa Fuze with rockbox installed

### Requirements

- python-kaa-metadata - Kaa Metadata is a Media Meta Data retrieval framework. It retrieves metadata from mp3, ogg, avi, jpg, tiff and other file formats. Among others it thereby parses ID3v2, ID3v1, EXIF, IPTC and Vorbis data into an object oriented struture. (http://freevo.org/kaa)

- python-dbus - simple interprocess messaging system (Python interface)

- ffmpeg - Multimedia player, server, encoder and transcoder (http://www.ffmpeg.org/)


## tagging_hook

This hook script adds episode title and podcast title to the audio file
The episode title is written into the title tag
The podcast title is written into the album tag

### Requirements

- python-mutagen - Mutagen is a Python module to handle audio metadata. (http://code.google.com/p/mutagen/)


## tfh_shownotes_hook

"Tin Foil Hat Show" is a podcast produced by CafeNinja.
http://cafeninja.blogspot.com/search/label/tinfoilhat

There is one special thing in this show. The show notes are hide in the FRONT_COVER image which is included in the mp3 file. This is the only place where you can find the show notes. So you have to run a few commands until you are able to read the notes.

This is the reason why I created some hooks to get this show notes automatically after I downloaded an episode with gPodder (http://gpodder.org/)

This github repository includes two options to configure your gPodder installation with this feature.

### Requirements

- python-eyed3 - eyeD3 is a Python module and program for processing ID3 tags (http://eyed3.nicfit.net/)

- steghide - Steghide is a steganography program that is able to hide data in various kinds of image- and audio-files. (http://steghide.sourceforge.net/)


## zpravy

The $subj podcast rss does not contain id and pubdate. Because of the missing guid gPodder reports always "no new episodes" for the podcast. 
This hook script fixes this. The pubdate can be calculated from the audio file url and I used the same number as guid.
