#!/usr/bin/python
# -*- coding: utf-8 -*-
import os.path
import unittest

from gpodder import api
from config import data
import rockbox_mp4_convert


class TestRockboxMP4Convert(unittest.TestCase):
    def setUp(self):
        self.client = api.PodcastClient()

        url = data.TEST_PODCASTS['TEDTalks']['url']
        episode_no = data.TEST_PODCASTS['TEDTalks']['episode']
        self.podcast = self.client.get_podcast(url)

        self.episode = self.podcast.get_episodes()[episode_no]
        self.filename = self.episode._episode.local_filename(create=False, check_only=True)

    def tearDown(self):
        self.client._db.close()

        converted_file = rockbox_mp4_convert.get_rockbox_filename(self.filename)
        if (os.path.exists(converted_file)):
            os.remove(converted_file)

    def test_file_renaming(self):
        self.assertIsNotNone(self.filename)
        self.assertEqual(os.path.basename(self.filename), 'MattCutts_2011U.mp4')
        self.assertEqual(rockbox_mp4_convert.get_rockbox_filename(self.filename),
            os.path.join(os.path.dirname(self.filename), 'MattCutts_2011U.mpg'))

    def test_calc_resolution(self):
        resolution = rockbox_mp4_convert.calc_resolution(512, 288, 224.0, 176.0)
        self.assertEqual(resolution, (224, 126))

        resolution = rockbox_mp4_convert.calc_resolution(1024, 768, 224.0, 176.0)
        self.assertEqual(resolution, (224, 168))

    def test_mp4convert(self):
        self.assertIsNotNone(self.filename)
        self.assertEqual(self.episode._episode.title, 'TED: Matt Cutts: Try something new for 30 days - Matt Cutts (2011)')

        new_filename = rockbox_mp4_convert.convert_mp4(self.filename)
        self.assertIsNotNone(new_filename)
        self.assertTrue(os.path.exists(new_filename))
