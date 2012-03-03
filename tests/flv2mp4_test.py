#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import shutil
import unittest

import gpodder

from config import data
import utils

EXTENSION_NAME = 'flv2mp4'
EXTENSION_FILE = os.path.join(os.environ['GPODDER_EXTENSIONS'], EXTENSION_NAME+'.py')


class TestFlv2Mp4(unittest.TestCase):
    def setUp(self):
        self.core, podcast_list = utils.init_test(
            EXTENSION_FILE,
            [(data.TEST_PODCASTS['drovics'], True),
             (data.TEST_PODCASTS['TinFoilHat'], True)
            ]
        )
        self.episode, self.filename, self.episode1, self.filename1 = podcast_list
        self.converted_file = os.path.splitext(self.filename)[0] + '.mp4'

        self.save_enabled = self.core.config.extensions.enabled
        self.core.config.extensions.enabled = [EXTENSION_NAME]

    def tearDown(self):
        self.core.config.extensions.enabled = self.save_enabled
        gpodder.user_extensions.shutdown()
        self.core.db.close()

        if os.path.exists(self.converted_file):
            os.remove(self.converted_file)

    def test_mp4convert(self):
        self.assertIsNotNone(self.filename)

        extension = gpodder.user_extensions.containers[0].module
        extension._run_conversion(self.episode)

        self.assertTrue(os.path.exists(self.converted_file))
        self.assertTrue(os.path.getsize(self.converted_file)>0)

    def test_context_menu(self):
        self.assertEqual(self.episode.mime_type, 'video/x-flv')
        self.assertNotEqual(self.episode1.mime_type, 'video/x-flv')

        self.assertTrue(gpodder.user_extensions.on_episodes_context_menu([self.episode,]))
        self.assertFalse(gpodder.user_extensions.on_episodes_context_menu([self.episode1,]))
