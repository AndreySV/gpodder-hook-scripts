#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import unittest

from gpodder import api
from config import data
from rename_downloads import rename_file


class TestRenameDownloads(unittest.TestCase):
    def setUp(self):
        self.client = api.PodcastClient()

        url = data.TEST_PODCASTS['TinFoilHat']['url']
        episodeno = data.TEST_PODCASTS['TinFoilHat']['episode']
        self.podcast = self.client.get_podcast(url)
        self.podcast_title = self.podcast.title

        self.episode = self.podcast.get_episodes()[episodeno]
        self.filename = self.episode._episode.local_filename(create=False, check_only=True)
        self.title = self.episode.title

    def tearDown(self):
        self.client._db.close()

    def test_rename_file(self):
        filename_test = os.path.join(os.environ['GPODDER_DOWNLOAD_DIR'],
            self.podcast_title, 'Pilot show.mp3')
        filename_new = rename_file(self.filename, self.title) 

        self.assertEqual(filename_test, filename_new)
        self.assertNotEqual(self.filename, filename_new)

