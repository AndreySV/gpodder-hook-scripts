#  -*- coding: utf-8 -*-
#
# Converts MP3 files to OGG format, makes time-stretching,
# apply some audio filters
# Fix some errors in broken mp3 files. 
#
# All functionality is imlemented in mp3_to_ogg.sh bash script.
# This bash script should be placed in user PATH. 
# 
# Requires: 
#     soxi,
#     sox, 
#     ogginfo, 
#     mp3info,
#     mp3check,
#     mp3val
#     mid3iconv,
#     notify-send,
# 
# For debug filters:
#     gnuplot
#
# Andrey Skvortsov <Andrej.Skvortzov@gmail.com>
#-----------------------------------------------------------


import gpodder

import os
import shlex
import subprocess

import logging
logger = logging.getLogger(__name__)

class gPodderHooks(object):
    def on_episode_downloaded(self, episode):
        self._convert_episode(episode)

    def _convert_episode(self, episode):
        filename = episode.local_filename(create=False)
        if filename is None:
            return
    
        (basename, extension) = os.path.splitext(filename)
        (path, basename) = os.path.split(basename)
        if episode.file_type() == 'audio' and ( extension.lower().endswith('mp3') or extension.lower().endswith('ogg') ):

            filename = filename.encode('utf-8')
            cmd = 'mp3_to_ogg.sh "%s" ' % filename 

            command_string = shlex.split(cmd)
            p = subprocess.Popen( command_string ,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            stdout, stderr = p.communicate()

            if p.returncode == 0:
                print(filename)
                new_filename = basename + '.ogg'
                full_new_filename = os.path.join( path, new_filename)
                print(new_filename)
                episode.filename = new_filename
                episode.calculate_filesize
                # episode.length = os.path.getsize(full_new_filename)
                episode.save()               
                logger.info('convert mp3 to ogg was successfull.')
                logger.debug(stderr)
                logger.debug(stdout)
            else:
                logger.info('convert mp3 to ogg was not successfull.')
                logger.debug(stderr)
                logger.debug(stdout)
                episode.delete_from_disk()
                episode.mark_new()


