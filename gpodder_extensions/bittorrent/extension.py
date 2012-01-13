#-*- coding: utf-8 -*-
# Automatically open .torrent files with a BitTorrent client
# Copy this script to ~/.config/gpodder/extensions/ to enable it.
# Thomas Perl <thp@gpodder.org>; 2010-10-11
import shlex
import subprocess

from gpodder.extensions import ExtensionParent

DEFAULT_CONFIG = {
    'bittorrent': {
        'enabled': True,
        'params': {
            'cmd': {
                'desc': u'Defines the command line bittorrent program:',
                'type': u'textitem',
                'value': u'transmission-cli %s',
            }
		}
    }
}


class gPodderExtensions(ExtensionParent):
    def __init__(self, config=DEFAULT_CONFIG, **kwargs):
        super(gPodderExtensions, self).__init__(config=config, **kwargs)

        self.test = kwargs.get('test', False)
        self.cmd = self.config.bittorrent.params.cmd.value
        self.check_command(self.cmd)

        if self.test:
            self.cmd = 'echo "%s"' % self.cmd

    def on_episode_downloaded(self, episode):
        if episode.extension() == '.torrent':
            self.notify_action("Downloading", episode)
            cmd = self.cmd % episode.local_filename(False)
            
            # Prior to Python 2.7.3, this module (shlex) did not
            # support Unicode input.
            if isinstance(cmd, unicode):
                cmd = cmd.encode('ascii', 'ignore')

            # for testing purpose it's possible to get to stdout+stderr
            # output
            p = subprocess.Popen(shlex.split(cmd), shell=False,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = p.communicate()

            if p.returncode == 0:
                self.notify_action("Downloading finished", episode)
            else:
                self.notify_action("Downloading finished with erros",
                    episode)
            
            if self.test:                
                return (stdout, stderr)
