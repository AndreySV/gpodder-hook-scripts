TEST_PODCASTS = {
    # rss feed contains all episodes from the beginning
    # selected episode should be 'dh-20091121-kurz-005.ogg'
    'DeimHart': {'url': 'http://deimhart.net/index.php?/feeds/categories/3-sendung-ogg.rss',
                 'episode': -12 },

    # rss feed contains all episodes from the beginning
    # selected episode should be 'TFH-001.mp3'
    'TinFoilHat': {'url': 'http://feeds.feedburner.com/TinFoilHat',
                   'episode': -1 },

    # rss feed don't contains all episodes
    # we don't have to download a epiosode for the tests
    'Zpravy': {'url': 'http://www2.rozhlas.cz/podcast/zpravy.php',
               'episode': None },
}
