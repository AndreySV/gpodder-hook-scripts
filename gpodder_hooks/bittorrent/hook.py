#-*- coding: utf-8 -*-
# Automatically open .torrent files with a BitTorrent client
# Copy this script to ~/.config/gpodder/hooks/ to enable it.
# Thomas Perl <thp@gpodder.org>; 2010-10-11
import shlex
import subprocess

from util import check_command


DEFAULT_PARAMS = {
    "bittorrent_cmd": {
        "desc": "Defines the command line bittorrent program:",
        "value": 'transmission-cli %s',
        "type": "textitem"
    }
}


class gPodderHooks(object):
    def __init__(self, params=DEFAULT_PARAMS, test=False):
        self.bittorrent_cmd = params['bittorrent_cmd']['value']
        self.test = test

        check_command(self.bittorrent_cmd)

        if test:
            self.bittorrent_cmd = 'echo "%s"' % self.bittorrent_cmd

    def on_episode_downloaded(self, episode):
        if episode.extension() == '.torrent':
            # Prior to Python 2.7.3, this module (shlex) did not support Unicode input.
            cmd = str(self.bittorrent_cmd % episode.local_filename(False))

            # for testing purpose it's possible to get to stdout+stderr output
            if self.test:
                p = subprocess.Popen(shlex.split(cmd), shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                return p.communicate()
            else:
                subprocess.Popen(shlex.split(cmd))
