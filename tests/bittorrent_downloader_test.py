#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import unittest

import gpodder

from config import data
import utils

EXTENSION_NAME = 'bittorrent_downloader'
EXTENSION_FILE = os.path.join(os.environ['GPODDER_EXTENSIONS'], EXTENSION_NAME+'.py')
TEST_OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test.out')


class TestBittorrent(unittest.TestCase):
    def setUp(self):
        self.core, podcast_list = utils.init_test(
            EXTENSION_FILE,
            [(data.TEST_PODCASTS['CRETorrent'], True)]
        )
        self.episode, self.filename = podcast_list

        test_cmd = 'cp "%s" ' + TEST_OUTPUT        
        self.core.config.extensions.bittorrent_downloader.cmd = test_cmd
        self.core.config.extensions.enabled = [EXTENSION_NAME]

    def tearDown(self):
        if os.path.exists(TEST_OUTPUT):
            os.remove(TEST_OUTPUT)

        self.core.shutdown()

    def test_shellcommand(self):
        self.assertIsNotNone(self.filename)
        self.assertIsNotNone(self.episode)

        gpodder.user_extensions.on_episode_downloaded(self.episode)
        self.assertTrue(os.path.exists(TEST_OUTPUT))
