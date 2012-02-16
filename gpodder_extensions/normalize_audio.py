# -*- coding: utf-8 -*-
# This extension adjusts the volume of audio files to a standard level
# Supported file formats are mp3 and ogg
#
# Requires: normalize-audio, mpg123
#
# (c) 2011-11-06 Bernd Schlapsi <brot@gmx.info>
# Released under the same license terms as gPodder itself.
import os
import shlex
import subprocess

import logging
logger = logging.getLogger(__name__)

import gpodder
from gpodder.util import sanitize_encoding
from gpodder.extensions import ExtensionParent

# Metadata for this extension
__id__ = 'normalize_audio'
__name__ = 'Normalize audio'
__desc__ = 'This hook adjusts mp3s/oggs so that they all have the same volume. It decode and re-encode the audio file'


PARAMS = {
    'context_menu': {
        'desc': u'add plugin to the context-menu',
        'type': u'checkbox',
    }
}

DEFAULT_CONFIG = {
    'extensions': {
        'normalize_audio': {
            'context_menu': True,
        }
    }
}

# a tuple of (extension, command)
SUPPORTED = (('ogg', 'normalize-ogg "%s"'), ('mp3', 'normalize-mp3 "%s"'))

#TODO: add setting to use normalize-audio instead of normalizie-mp3 for mp3 files if wanted
# http://normalize.nongnu.org/README.html FAQ #5
#MP3_CMD = 'normalize-audio "%s"'

CMDS_TO_TEST = ('normalize-ogg', 'normalize-mp3', 'normalize-audio',
    'lame', 'mpg123', 'oggenc', 'oggdec')


class gPodderExtension(ExtensionParent):
    def __init__(self, config=DEFAULT_CONFIG, **kwargs):
        super(gPodderExtension, self).__init__(config=config, **kwargs)
        self.context_menu_callback = self._convert_episodes

        for cmd in CMDS_TO_TEST:
            self.check_command(cmd)

    def on_episode_downloaded(self, episode):
        self._convert_episode(episode)

    def _show_context_menu(self, episodes):
        if not self.config.context_menu:
            return False

        mimetypes = [e.mime_type for e in episodes if e.mime_type is not None
            and self.get_filename(e)]
        if 'audio/ogg' not in mimetypes and 'audio/mpeg' not in mimetypes:
            return False
        return True

    def _convert_episode(self, episode):
        filename = episode.local_filename(create=False, check_only=True)
        if filename is None:
            return

        formats, commands = zip(*SUPPORTED)
        (basename, extension) = os.path.splitext(filename)
        extension = extension.lstrip('.').lower()
        if episode.file_type() == 'audio' and extension in formats:
            self.notify_action("Normalizing", episode)

            cmd = commands[formats.index(extension)] % filename

            # Prior to Python 2.7.3, this module (shlex) did not support Unicode input.
            cmd = sanitize_encoding(cmd)

            p = subprocess.Popen(shlex.split(cmd),
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = p.communicate()

            if p.returncode == 0:
                logger.info('normalize-audio processing successfull.')
                self.notify_action("Normalizing finished successfully", episode)

            else:
                logger.info('normalize-audio processing not successfull.')
                self.notify_action("Normalizing finished not successfully", episode)
                logger.debug(stderr)

    def _convert_episodes(self, episodes):
        for episode in episodes:
            self._convert_episode(episode)
