# Hey emacs -*- coding: utf-8 -*-
#  
# Autodownload new episodes only for selected podcast feeds
#
# On posix systems 'zenity' is necessary. User will be asked 
# after addition new feed should be downloaded new episodes of 
# the feed automaticaly or not. 
# 
# On other systems new episodes will not be downloaded 
# automaticaly by default. To switch autodownload feature on
# user need to open auto_download.sqlite database with any db-client
# and change where necessary records.
# 
# Andrey Skvortsov <Andrej.Skvortzov@gmail.com>
#

import gpodder

import gtk

import os
import os.path
import shlex
import subprocess
import sqlite3
import dbus
import multiprocessing

from gpodder.liblogger import log

_ = gpodder.gettext
N_ = gpodder.ngettext


#import logging
#logger = logging.getLogger(__name__)




class gPodderHooks(object):
    def on_podcast_updated(self, podcast):
        self._process_hook(podcast)

    def _process_hook(self, podcast):
        auto = self.check_download( podcast )
        if auto:
            self.auto_download( podcast )

    def open_database(self):
        database=os.path.expanduser('~')+'/.config/gpodder/auto_download.sqlite'
        con = sqlite3.connect(database, check_same_thread = False)

        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS Podcasts(Id INTEGER PRIMARY KEY, Title TEXT, Description TEXT, url TEXT, auto_download INTEGER);")
        con.commit()
        return con

    def ui_auto_download_question(self, podcast):
    #        log('Info: new podcast is found: %s', podcast.title.decode("utf-8")

        if os.name == 'posix':
            title = "New podcast is found: "
            cmd = "$(sleep 2 && "
            cmd = cmd + "wmctrl -a " + title + "-b add,above && "
            cmd = cmd + "wmctrl -a " + title + " ) &"
            # print cmd
            os.system( cmd )
            
            cmd ="zenity --question --timeout 10 "
            cmd = cmd + "--window-icon /usr/share/pixmaps/gpodder.png "
            cmd = cmd + "--title '" + title  + podcast.title.decode("utf-8") + "' "
            cmd = cmd + " --text 'Do you want automatically download new episodes of the podcast?'"
            print cmd
            ret = os.WEXITSTATUS( os.system( cmd ) )
            if ret == 0:
                auto = 1
            elif ret == 1:
                auto = 0
            else:
                auto = 'ask_later'
        else:
            auto = 0

        return auto


    def check_download(self, podcast):
        con = self.open_database()
        cur = con.cursor()
        url = podcast.url.decode("utf-8")
        cur.execute("SELECT auto_download FROM Podcasts WHERE url=?", (url,))
        row = cur.fetchone()
        if not row:
            print 'not found'

            auto = self.ui_auto_download_question( podcast )
            if auto != 'ask_later':
                id = podcast.id
                title = podcast.title.decode("utf-8")
                description = podcast.title.decode("utf-8")

                cur.execute('DELETE FROM Podcasts WHERE id=?', (id,))
                cur.execute('INSERT INTO Podcasts VALUES( ?, ?, ?, ?, ? )', (id, title, description, url, auto) )
                con.commit()

        else:
            auto = row[0]
        return auto

    def auto_download(self, podcast):
        episodes = podcast.get_new_episodes()
        bus = dbus.SessionBus()
        proxy = bus.get_object('org.gpodder', '/podcasts')
        gpodder_iface = dbus.Interface(proxy, dbus_interface='org.gpodder.podcasts')
        urls=[]
        for episode in episodes:
            if episode.check_is_new():
                urls.append(episode.url)
        props = gpodder_iface.play_or_download_episode(urls)
