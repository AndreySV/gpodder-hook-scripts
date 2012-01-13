# -*- coding: utf-8 -*-
# Convertes m4a audio files to mp3
# This requires ffmpeg to be installed. Also works as a context
# menu item for already-downloaded files.
#
# (c) 2011-11-23 Bernd Schlapsi <brot@gmx.info>
# Released under the same license terms as gPodder itself.

import gpodder
from gpodder.extensions import ExtensionParent

import os
import shlex
import subprocess

import logging
logger = logging.getLogger(__name__)


DEFAULT_CONFIG = {
    'm4a_converter': {
        'enabled': False,
        'params': {
            'file_format': {
                'desc': u'Target file format:',
                'type': u'radiogroup',
                'list': ( 'mp3', 'ogg' ),
                'value': [ True, False ],
            },
            'context_menu': {
                'desc': 'add plugin to the context-menu',
                'type': 'checkbox',
                'value': True,
            }   
        }
    }
}

FFMPEG_CMD = 'ffmpeg -i "%(infile)s" -sameq "%(outfile)s"'
MIME_TYPES = ['audio/x-m4a', 'audio/mp4']


class gPodderExtensions(ExtensionParent):
    def __init__(self, config=DEFAULT_CONFIG, **kwargs):
        super(gPodderExtensions, self).__init__(config=config, **kwargs)
        self.context_menu_callback = self._convert_episodes

        choices = zip(self.config.m4a_converter.params.file_format.list,
            self.config.m4a_converter.params.file_format.value)
        self.extension = '.' + [ext for ext, state in choices if state][0]

        self.test = kwargs.get('test', False)
        self.check_command(FFMPEG_CMD)

    def on_episode_downloaded(self, episode):
        self._convert_episode(episode)

    def _show_context_menu(self, episodes):
        if not self.config.m4a_converter.params.context_menu.value:
            return False

        episodes = [e for e in episodes if e.mime_type in MIME_TYPES]
        if not episodes:
            return False
        return True 

    def _convert_episode(self, episode):
        filename = episode.local_filename(create=False)
        dirname = os.path.dirname(filename)
        basename, ext = os.path.splitext(os.path.basename(filename))
        new_filename = basename + self.extension

        if episode.mime_type not in MIME_TYPES:
            return

        self.notify_action("Converting", episode)
        
        target = os.path.join(dirname, new_filename)
        cmd = FFMPEG_CMD % {
            'infile': filename,
            'outfile': target 
        }

        # Prior to Python 2.7.3, this module (shlex) did not support Unicode input.
        if isinstance(cmd, unicode):
            cmd = cmd.encode('ascii', 'ignore')
            
        ffmpeg = subprocess.Popen(shlex.split(cmd),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = ffmpeg.communicate()

        if ffmpeg.returncode == 0:
            logger.info('m4a -> %s conversion successful.', self.extension)
            self.notify_action("Converting finished", episode)
            if not self.test:
                self.update_episode_file(episode, new_filename)
                os.remove(filename)
        else:
            logger.info('Error converting file. FFMPEG installed?')
            self.notify_action("Converting finished with errors", episode)
            try:
                os.remove(target)
            except OSError:
                pass

    def _convert_episodes(self, episodes):
        for episode in episodes:
            self._convert_episode(episode)
