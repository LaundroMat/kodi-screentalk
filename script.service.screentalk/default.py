import os
import sys

from resources.player import XBMCPlayer
from resources.settings import __addonname__, get_setting
from services.stream_listener import TwitterStreamListener
from services.logging import log
import xbmc


# import rpdb2
# rpdb2.start_embedded_debugger('pw')

# Set directories for python 3rd party module imports.
# Thanks http://stackoverflow.com/questions/24421213/importing-a-module-in-resources-into-an-xbmc-plugin
path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(path, 'resources', 'lib', 'services'))

from resources.service import ScreentalkService

twitter_stream_listener = TwitterStreamListener()

class XBMCMonitor(xbmc.Monitor):
    def __init__(self, *args, **kwargs):
        super(XBMCMonitor, self).__init__(*args, **kwargs)

    def onSettingsChanged(self):
        log("Detected change in settings.")
        twitter_username = get_setting('twitter_username')
        if twitter_username[0] != '@':
            twitter_username = '@{0}'.format(twitter_username)

        log("Username changed to {0}.".format(twitter_username))

        twitter_stream_listener.follow(twitter_username)

if __name__ == '__main__':
    dataroot = xbmc.translatePath('special://profile/addon_data/%s' % __addonname__).decode('utf-8')
    if os.path.exists(dataroot) is False:
        # This means it's the first time the add-on is being used
        os.mkdir(dataroot)
        xbmc.executebuiltin('Addon.OpenSettings(%s)' % __addonname__)

    username = get_setting('twitter_username')

    if username != "@":
        twitter_stream_listener.follow(username)

    service = ScreentalkService()
    player = XBMCPlayer(service=service)
    monitor = XBMCMonitor()

    service.player = player

    service.run()
