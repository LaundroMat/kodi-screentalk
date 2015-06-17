import json
import os
import io

import requests
import tweepy

from resources.lib import fractional_seconds
from resources.lib.fractional_seconds import convert_time_string_to_fractional_seconds
from resources.lib.tweepy.error import TweepError
from resources.lib.tweepy.streaming import StreamListener
from resources.twitter import Twitter
from services.config import SCREENTALK_API
from services.kodi_calls import get_video_player_id, get_timestamp, get_item_info, get_screenshot
from services.logging import log
from services.snapshot import Snapshot
import xbmc


class TwitterStreamListener(StreamListener):
    """ A listener handles tweets are the received from the stream.
    """
    def __init__(self, username=None):
        super(TwitterStreamListener, self).__init__()
        self.twitter = Twitter()
        self.stream = tweepy.Stream(self.twitter.auth, self)
        if username:
            self.follow(username)

    def disconnect(self):
        self.stream.disconnect()

    def follow(self, username):
        # get twitter_user_id of user
        try:
            twitter_user_id = self.twitter.api.get_user(username).id
        except:
            #TODO Notify user on screen if following doesn't work (probably twitter error?)
            twitter_user_id = ""
        log("Twitter user ID is {id}.".format(id=twitter_user_id))

        try:
            self.stream.filter(follow=[str(twitter_user_id)], async=True)  # Follow this user: whenever he tweets while the video is playing, snapshots are uploaded
        except:
            # Already connected - Can't catch TweepError apparently :(
            self.stream.disconnect()
            self.stream = tweepy.Stream(self.twitter.auth, self)
            self.stream.filter(follow=[str(twitter_user_id)], async=True)  # Follow this user: whenever he tweets while the video is playing, snapshots are uploaded
        finally:
            log("Started following twitter stream of {username}.".format(username=username))

    def on_status(self, status):
        log("Status received: {status}".format(status=status))

    def on_data(self, data):
        # TODO: use on_status instead...
        log("Stream tweet received:")
        tweet_data = json.loads(data)
        log(tweet_data)

        snapshot = Snapshot()  # Create snapshot to store info about video, position, etc.

        player_id = get_video_player_id()

        if player_id:
            snapshot.position = get_timestamp(player_id)

            log("Video position: {pos}".format(pos=snapshot.position))

            item_playing_info = get_item_info(player_id)
            snapshot.type = item_playing_info.get('type')
            _, snapshot.filename = os.path.split(item_playing_info.get('file'))
            snapshot.imdbnumber = item_playing_info.get('imdbnumber')
            if snapshot.type == "movie":
                snapshot.title = item_playing_info.get('title')
            elif snapshot.type == "episode":
                snapshot.title = item_playing_info.get("showtitle")
                snapshot.episode = item_playing_info.get("episode")
                snapshot.season = item_playing_info.get("season")

            # snapshot.type = "movie" if xbmc.getInfoLabel('VideoPlayer.Title') else "episode"
            # snapshot.filename = xbmc.getInfoLabel('Player.Filename')
            # # snapshot.imdbnumber = xbmc.getInfoLabel()
            # if snapshot.type == "movie":
            #     snapshot.title = xbmc.getInfoLabel('VideoPlayer.Title')
            # else:
            #     snapshot.title = xbmc.getInfoLabel('VideoPlayer.TVShowTitle')
            #     snapshot.episode = xbmc.getInfoLabel('VideoPlayer.Episode')
            #     snapshot.season = xbmc.getInfoLabel('VideoPlayer.Season')

            log("Video filename:\t%s" % snapshot.filename)

            # xbmc.executebuiltin('XBMC.TakeScreenshot') won't work
            # Needs screenshot folder set & there's no way to find out what it is.

            # Get screenshot
            screenshot = get_screenshot()

            url = SCREENTALK_API + '/capture/new/'

            if 'delete' in tweet_data.keys():
                log("Tweet data was deleted.")
            else:
                # Get twitter status ID to link to snapshot
                snapshot.twitter_status_id = tweet_data.get('id')
                snapshot.twitter_username = tweet_data.get('user').get('name')
                snapshot.twitter_user_id = tweet_data.get('user').get('id')
                snapshot.twitter_status_body = tweet_data.get('text')

                log("Trying to post following data to %s" % url)
                log(snapshot.as_json())

                try:
                    r = requests.post(
                        url,
                        files={'file': io.BytesIO(screenshot)},
                        data={'json': snapshot.as_json()}
                    )
                except Exception, e:
                    log("Error when posting screenshot:")
                    log(e)
                else:
                    log("Response: {content}".format(content=r.content))


                # Alternative:
                # (maybe put in a queue kind of service if POSTing binary data proves to be too bandwith intensive?
                # Save the image and upload it as a file to our webservice
                # save_path = os.path.join(dataroot, "image.bin")
                # log("Saving screenshot bytes to %s." % save_path)
                # f = open(save_path, "wb")
                # f.write(screenshot)
                # f = open(save_path, "rb")
                # r = requests.post(url, files=f, data={'test': 'olei'})
                # log(screenshot)  -> screenshot = bytearray...
        else:
            log("No player id...")
        return True

    def on_error(self, status):
        log("A TwitterStreamListener error has occurred...")
        log(status)