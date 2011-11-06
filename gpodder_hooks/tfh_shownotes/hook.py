#!/usr/bin/python
# -*- coding: utf-8 -*-
####
# 10/2010 Bernd Schlapsi <brot@gmx.info>
#
# This script is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
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
# * python-eyed3 (eyeD3 python library - http://eyed3.nicfit.net/)
# * steghide (steganography program - http://steghide.sourceforge.net/)
#
# The script extract the shownotes from the "Tin Foil Hat" podcast
# You can find the instructions how to extract shownotes for the
# "Tin Foil Hat" podcast here:
# http://cafeninja.blogspot.com/2010/10/tin-foil-hat-show-episode-001.html

import eyeD3
import os
import shlex
import subprocess
import tempfile

import logging
logger = logging.getLogger(__name__)

import gpodder
from metadata import metadata
from util import check_command


DEFAULT_PARAMS = { 
    "context_menu": {
        "desc": u"add plugin to the context-menu",
        "value": True,
        "type": u"checkbox",
        "sort": 1
    }   
}

TFH_TITLE = 'Tin Foil Hat'
STEGHIDE_CMD = 'steghide extract -f -p %(pwd)s -sf %(img)s -xf %(file)s'


def extract_image(filename):
    """extract image from the podcast file"""
    imagefile = None
    try:
        if eyeD3.isMp3File(filename):
            tag = eyeD3.Mp3AudioFile(filename).getTag()
            images = tag.getImages()
            if images:
                tempdir = tempfile.gettempdir()
                img = images[0]
                imagefile = img.getDefaultFileName()
                img.writeFile(path=tempdir, name=imagefile)
                imagefile = "%s/%s" % (tempdir, imagefile)
            else:
                logger.info(u'No image found in %s' % filename)
    except:
        pass

    return imagefile


def extract_shownotes(imagefile, remove_image=True):
    """extract shownotes from the FRONT_COVER.jpeg"""
    shownotes = None
    password = 'tinfoilhat'
    shownotes_file = '/tmp/shownotes.txt'

    if not os.path.exists(imagefile):
        return shownotes

    cmd = STEGHIDE_CMD % {
        'pwd': password,
        'img': imagefile,
        'file': shownotes_file
    }
    myprocess = subprocess.Popen(shlex.split(cmd),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout, stderr) = myprocess.communicate()

    if remove_image:
        os.remove(imagefile)

    if myprocess.returncode == 0:
        #read shownote file
        f = open(shownotes_file, 'r')
        shownotes = unicode(f.read(), "utf-8")
        f.close()
    else:
        logger.error(u'Error extracting shownotes from the image file %s' % imagefile)

    return shownotes


class gPodderHooks(object):
    def __init__(self, params=DEFAULT_PARAMS):
        logger.info('"Tin Foil Hat" shownote extractor extension is initializing.')
        self.params = params

        check_command(STEGHIDE_CMD)

    def _download_shownotes(self, episodes):
        for episode in episodes:
            self.on_episode_downloaded(episode)

    def _show_context_menu(self, episodes):
        if not self.params['context_menu']:
            return False

        if TFH_TITLE not in [e.channel.title for e in episodes]:
            return False
        return True 

    def on_episodes_context_menu(self, episodes):
        if self._show_context_menu(episodes):
            return [(metadata['name'], self._download_shownotes)]

    def on_episode_downloaded(self, episode):
        if episode.chanel.title == TFH_TITLE:
            filename = episode.local_filename(create=False, check_only=True)
            if filename is None:
                return
            
            imagefile = extract_image(filename)
            if imagefile is None:
                return

            shownotes = extract_shownotes(imagefile)
            if shownotes is None:
                return

            # save shownotes in the database
            if episode.description.find(shownotes) == -1:
                episode.description = "%s\n\n<pre>%s</pre>" % (episode.description, shownotes)
                episode.save()
                episode.db.commit()
                logger.info(u'updated shownotes for podcast: (%s/%s)' % (episode.channel.title, episode.title))
