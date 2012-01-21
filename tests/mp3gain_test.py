#!/usr/bin/python
# -*- coding: utf-8 -*-
import filecmp
import shutil 
import unittest

from gpodder import api
from config import data
from utils import get_episode, get_metadata
from mp3gain import extension


class TestMp3Gain(unittest.TestCase):
    def setUp(self):
        self.client = api.PodcastClient()
        (self.ogg_episode, self.ogg_file, self.ogg_file_save) = self.read_episode(
                data.TEST_PODCASTS['DeimHart'])

        (self.mp3_episode, self.mp3_file, self.mp3_file_save) = self.read_episode(
                data.TEST_PODCASTS['TinFoilHat'])

        self.metadata = get_metadata(extension)

    def tearDown(self):
        self.client._db.close()
        shutil.move(self.mp3_file_save, self.mp3_file)
        shutil.move(self.ogg_file_save, self.ogg_file)

    def read_episode(self, podcast_config):
        episode, filename = get_episode(self.client, podcast_config, True)
        filename_save = '%s.save' % filename 
        shutil.copyfile(filename, filename_save)

        return(episode, filename, filename_save)

    def test_mp3_file(self):
        self.assertTrue(filecmp.cmp(self.mp3_file, self.mp3_file_save))

        norm_extension = extension.gPodderExtensions(metadata=self.metadata)
        norm_extension._convert_episode(self.mp3_episode._episode)

        self.assertFalse(filecmp.cmp(self.mp3_file, self.mp3_file_save))

    def test_ogg_file(self):
        self.assertTrue(filecmp.cmp(self.ogg_file, self.ogg_file_save))

        norm_extension = extension.gPodderExtensions(metadata=self.metadata)
        norm_extension._convert_episode(self.ogg_episode._episode)

        self.assertTrue(filecmp.cmp(self.ogg_file, self.ogg_file_save))

    def test_context_menu(self):
        norm_extension = extension.gPodderExtensions(metadata=self.metadata)
        self.assertTrue(norm_extension._show_context_menu([self.mp3_episode._episode,]))
        self.assertFalse(norm_extension._show_context_menu([self.ogg_episode._episode,]))

