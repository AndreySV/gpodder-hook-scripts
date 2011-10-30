# -*- coding: utf-8 -*-
# Rename files after download based on the episode title
# Copyright (c) 2011-04-04 Thomas Perl <thp.io>
# Licensed under the same terms as gPodder itself

from gpodder import util

import os

import logging
logger = logging.getLogger(__name__)


def rename_file(current_filename, title):
    dirname = os.path.dirname(current_filename)
    filename = os.path.basename(current_filename)
    basename, ext = os.path.splitext(filename)

    new_filename = util.sanitize_encoding(title) + ext
    return os.path.join(dirname, new_filename)
    

class gPodderHooks(object):
    def on_episode_downloaded(self, episode):
        current_filename = episode.local_filename(create=False)

        new_filename = rename_file(current_filename, episode.title)
        logger.info('Renaming:', current_filename, '->', new_filename)

        os.rename(current_filename, new_filename)
        episode.filename = new_filename
        episode.save()
