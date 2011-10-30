#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
import os
import unittest
import urllib2

from gpodder import api
from config import data
import cmml_creator

LINUXOUTLAWS_FILENAME='linuxoutlaws230.ogg'

def create_cmml_from_file(ogg_file):
    m = re.match('(.*linuxoutlaws)([0-9]+)\\.(ogg|mp3)',ogg_file)
    if m is not None:
        episode_num = m.group(2)
        url = 'http://sixgun.org/linuxoutlaws/' + episode_num
        page = urllib2.urlopen(url)
        cmml_creator.create_cmml_linux_outlaws(page, ogg_file)
    else:
        print("not a Linux Outlaws file !")


def delete_cmml_file(filename):
    cmml_file = cmml_creator.get_cmml_filename(filename)
    if os.path.exists(cmml_file):
        os.remove(cmml_file)


class TestCmmlLinuxOutlaws(unittest.TestCase):
    def setUp(self):
        self.client = api.PodcastClient()

        url = data.TEST_PODCASTS['LinuxOutlaws']['url']
        self.podcast = self.client.get_podcast(url)

        self.episode = self.podcast.get_episodes()[-1]
        self.filename = self.episode._episode.local_filename(create=True)

    def tearDown(self):
        delete_cmml_file(LINUXOUTLAWS_FILENAME)
        delete_cmml_file(self.filename)
        self.client._db.close()

    def test_create_cmml(self):
        cmml_file = cmml_creator.get_cmml_filename(LINUXOUTLAWS_FILENAME)
        create_cmml_from_file(LINUXOUTLAWS_FILENAME)
        self.assertTrue(os.path.exists(cmml_file))
        self.assertTrue(os.path.getsize(cmml_file)>0)

    def test_create_cmml_hook(self):
        cmml_hook = cmml_creator.gPodderHooks()
        cmml_hook.on_episode_downloaded(self.episode._episode)
        cmml_file = cmml_creator.get_cmml_filename(self.filename)
        self.assertTrue(os.path.exists(cmml_file))
        self.assertTrue(os.path.getsize(cmml_file)>0)
