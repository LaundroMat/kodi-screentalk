import os
import sys
import xbmc

# Set directories for python 3rd party module imports.
# Thanks http://stackoverflow.com/questions/24421213/importing-a-module-in-resources-into-an-xbmc-plugin
path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(path, 'lib'))
from services.logging import log


class XBMCPlayer(xbmc.Player):
    def __init__(self, service, *args, **kwargs):
        super(XBMCPlayer, self).__init__(*args, **kwargs)
        self.service = service
        self.paused = None

    def onPlayBackStarted(self):
        log('Playback started at %f' % self.getTime())
        self.paused = False
        self.service.on_playback_started_or_resumed()

    def onPlayBackPaused(self):
        self.paused = True
        log('Playback paused at %f' % self.getTime())

    def onPlayBackResumed(self):
        log('Playback resumed at %f' % self.getTime())
        self.paused = False
        self.service.on_playback_started_or_resumed()

    def onPlayBackStopped(self):
        self.paused = False
        log('Playback stopped.')

    def onPlayBackEnded(self):
        self.paused = False
        log('Playback ended.')