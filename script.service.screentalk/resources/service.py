import os
import threading
import time
import sys
import tweepy
from resources.settings import get_setting

from resources.dialog import Dialog
from resources.twitter import Twitter
import xbmc
import xbmcaddon
import xbmcgui

__addon__ = xbmcaddon.Addon()
__addonpath__ = __addon__.getAddonInfo('path').decode('utf-8')

_ADDON_NAME = 'script.service.screentalk'
_addon = xbmcaddon.Addon(id=_ADDON_NAME)


MATCH_TYPE = get_setting("match_type")

# Set directories for python 3rd party module imports.
# Thanks http://stackoverflow.com/questions/24421213/importing-a-module-in-resources-into-an-xbmc-plugin
path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(path, 'lib'))
from services.logging import log
import requests
from services import config
from services.config import SCREENTALK_HOST, SCREENTALK_API



class ScreenConversation(object):
    """
        Contains the tweets for a specific title
    """
    def __init__(self, title):

        self.title = title
        self.items = []

        self.create_conversation()

    def __len__(self):
        return len(self.items)

    def load_conversation_from_web(self, title=''):
        data = []
        log("Downloading conversation for {title}.".format(title=title))
        log("Calling %s " % SCREENTALK_API + '/video/tweets/')
        try:
            r = requests.get(SCREENTALK_API + '/video/tweets/', params={'q': title})
        except:
            # Strange, but neither requests.exceptions.ConnectionError, ConnectionError or requests.ConnectionError are caught...
            # Defaulting to catching a general exception then :(
            raise ScreentalkConnectionError
        else:
            data = r.json().get('tweets', [])
            log('{numtweets} tweets downloaded from webservice.'.format(numtweets=len(data)))
            return data

    def create_conversation(self):
        tweet_data = self.load_conversation_from_web(self.title)
        self.items = [VideoTweet(**data) for data in tweet_data]
        self.items = [item for item in self.items if item.twitter_status_id]
        self.items = sorted(self.items, key=lambda i: i.position)


class VideoTweet(object):
    def __init__(self, position, twitter_status_id):
        self.api = Twitter().api
        self.position = position
        self.twitter_status_id = twitter_status_id
        self.fetch_twitter_data()

    def fetch_twitter_data(self):
        # Fetch tweet status data, asynchronously
        def fetch_async():
            status = self.download_status_data(self.twitter_status_id)
            if status:
                self.status = {
                    'text': status.text,
                    'user_screen_name': '@{user}'.format(user=status.user.screen_name),
                    'user_profile_image_url': status.user.profile_image_url
                }
                # Download the user profile image
                image_path = self.download_user_profile_image(status.user.profile_image_url)
                if image_path:
                    self.status['user_profile_image_file'] = image_path
                    log("Saved profile image file to %s" % image_path)
            else:
                # No status found (probably invalid status_id)
                self.status = self.twitter_status_id = None # Will be pruned later because it's empty

        fetch = threading.Thread(target=fetch_async())
        fetch.start()

    def download_status_data(self, status_id):
        """
            Calls twitter and receives status object.
            interesting are:
                status.text
                status.user.screen_name
                status.user.profile_image_url
        """
        log("Fetching twitter data for status id: %s" % status_id)
        try:
            status = self.api.get_status(status_id)
        except tweepy.TweepError, e:     # For one reason or another, TweepError is not being caught...
            log("Tweepy raised an exception while fetching status {status_id}".format(status_id=status_id))
            log("{exception}".format(exception=str(e)))
            status = None
        return status

    def download_user_profile_image(self, url):
        r = requests.get(url, stream=True)
        image_path = os.path.join(__addonpath__, url.split('/')[-1])
        if r.status_code == 200:
            with open(image_path, 'wb') as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)
            return image_path


class ScreentalkConnectionError(Exception):
    def __init__(self, message, errors):
        # Call the base class constructor with the parameters it needs
        super(ScreentalkConnectionError, self).__init__(message)

        # Warn user & log problem
        display_xbmc_notification(
            message='Web service unavailable; service is not running.',
            notification_type=xbmcgui.NOTIFICATION_WARNING
        )

        log("Error connection to screentalk webservice.")


class ScreentalkWebserviceAdapter(object):
    def __init__(self):
        self.url = SCREENTALK_API

    @property
    def is_alive(self):
        try:
            r = requests.get(self.url + "/alive")
        except requests.ConnectionError, requests.Timeout:
            display_xbmc_notification(
                message='Screentalk webservice is unavailable.',
                notification_type=xbmcgui.NOTIFICATION_WARNING
            )
            return False
        else:
            return True


def display_xbmc_notification(message, notification_type):
    dialog = xbmcgui.Dialog()
    dialog.notification(
        "ScreenTalk",
        message,
        notification_type,
        5000
    )


class ScreentalkService(object):
    def __init__(self):
        self.conversation = None
        self.player = None
        self.dialogs = []
        self.position_filter_start = 0.0
        self.position_filter_end = 0.0
        self.webservice = ScreentalkWebserviceAdapter()

        self.monitor = xbmc.Monitor()

        super(ScreentalkService, self).__init__()

    def run(self):
        log("ScreentalkService is running.")
        while True:
            if self.player.isPlayingVideo():
                self.set_position_boundaries()
                self.manage_dialogs(self.get_tweets_for_current_position())

            if self.monitor.waitForAbort(0.1):  # an xbmc.Monitor method
                break

    def on_playback_started_or_resumed(self):
        """
            Called on XBMCPlayer's OnPlaybackStarted or OnPlaybakcResumed
        """
        self.conversation = ScreenConversation(xbmc.getInfoLabel('Player.Title'))   # Renew the conversation (ie get data from webservice)
        log('Found {num} conversation items for this video.'.format(num=len(self.conversation)))
        display_xbmc_notification(
            message='Got {amount} tweet(s) for this video & I\'m capturing yours.'.format(amount=len(self.conversation.items)),
            notification_type=xbmcgui.NOTIFICATION_INFO
        )

    def get_tweets_for_current_position(self):
        try:
            items = [item for item in self.conversation.items if self.position_filter_end >= item.position >= self.position_filter_start]
        except AttributeError:
            # self.converstation is None because loading hasn't finished yet
            return []
        else:
            return items

    def set_position_boundaries(self):
        try:
            # log("Current position {current_pos}.".format(current_pos=self.getTime()))
            self.position_filter_start = 0.0 + self.position_filter_end
            self.position_filter_end = self.player.getTime()
        except RuntimeError as e:
            # Typical error here is that player just stopped but we don't know it yet
            log("Error setting positions - probably the video was stopped and I don't know it yet.")
            log(e.message)
            log(e.args)

    def manage_dialogs(self, tweets_to_display):
        for tweet in tweets_to_display:
            self.dialogs.append(self.create_and_display_dialog(tweet))

        # Remove dialogs from list if older than DIALOG_LIFESPAN
        self.dialogs = filter(lambda d: d.creation_time >= time.time()-config.DIALOG_LIFESPAN_SECONDS, self.dialogs)

    def create_and_display_dialog(self, tweet):
        dialog = Dialog(tweet, len(self.dialogs)+1)
        dialog.show()
        return dialog

