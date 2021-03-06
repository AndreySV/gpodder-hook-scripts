#!/usr/bin/python
# -*- coding: utf-8 -*-
####
# 01/2011 Bernd Schlapsi <brot@gmx.info>
#
# This script is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# gPodder is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Dependencies:
# * python-mutagen (Mutagen is a Python module to handle audio metadata)
#
# This hook script adds episode title and podcast title to the audio file
# The episode title is written into the title tag
# The podcast title is written into the album tag

import datetime
import os
import gpodder

import logging
logger = logging.getLogger(__name__)

try:
    from mutagen import File 
    mutagen_installed = True
except:
    logger.error( '(tagging hook) Could not find mutagen')
    mutagen_installed = False


## settings
strip_album_from_title = True
genre_tag = u'Podcast'


def read_episode_info(episode):
    info = {
        'filename': None,
        'album': None,
        'title': None,
        'pubDate': None
    }

    # read filename (incl. file path) from gPodder database
    info['filename'] = episode.local_filename(create=False, check_only=True)
    if info['filename'] is None:
        return

    # read title+album from gPodder database
    info['album'] = episode.channel.title
    title = episode.title
    if (strip_album_from_title and title and info['album'] and title.startswith(info['album'])):
        info['title'] = title[len(info['album']):].lstrip()
    else:
        info['title'] = title

    # convert pubDate to string
    try:
        pubDate = datetime.datetime.fromtimestamp(episode.pubDate)
        info['pubDate'] = pubDate.strftime('%Y-%m-%d %H:%M')
    except:
        try:
            # since version 3 the published date has a new/other name
            pubDate = datetime.datetime.fromtimestamp(episode.published)
            info['pubDate'] = pubDate.strftime('%Y-%m-%d %H:%M')
        except:
            info['pubDate'] = None

    return info


def write_info2file(info):
    # open file with mutagen
    audio = File(info['filename'], easy=True)
    if audio is None:
        return

    # write title+album information into audio files
    if audio.tags is None:
        audio.add_tags()

    # write album+title
    if info['album'] is not None:
        audio.tags['album'] = info['album']
    if info['title'] is not None:
        audio.tags['title'] = info['title']

    # write genre tag
    if genre_tag is not None:
        audio.tags['genre'] = genre_tag
    else:
        audio.tags['genre'] = ''

    # write pubDate
    if info['pubDate'] is not None:
        audio.tags['date'] = info['pubDate']

    audio.save()


class gPodderHooks(object):
    def __init__(self):
        logger.info('tagging extension is initializing.')

    def on_episode_downloaded(self, episode):
        # exit if mutagen is not installed
        if not mutagen_installed:
            return

        info = read_episode_info(episode)
        write_info2file(info)

        logger.info(u'tagging.on_episode_downloaded(%s/%s)' % (episode.channel.title, episode.title))
