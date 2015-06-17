import json
from services.logging import log


class Snapshot(object):
    def __init__(self):
        log("New Snapshot instance created.")
        self.id = None
        self.twitter_status_id = None
        self.twitter_username = None
        self.twitter_user_id = None
        self.twitter_status_body = None
        self.filename = ""
        self.type = None
        self.title = ""
        self.position = {}
        self.episode = None
        self.season = None
        self.imdbnumber = None

    def as_json(self):
        return_value = {
            'twitter_status_id': self.twitter_status_id,
            'twitter_username': self.twitter_username,
            'twitter_user_id': self.twitter_user_id,
            'twitter_status_body': self.twitter_status_body,
            'type': self.type,
            'filename': self.filename,
            'title': self.title,
            'imdbnumber': self.imdbnumber,
            'position': {
                'hours': self.position.get('hours'),
                'minutes': self.position.get('minutes'),
                'seconds': self.position.get('seconds'),
                'milliseconds': self.position.get('milliseconds')
            }
        }

        if self.type == "episode":
            return_value.update({
                'episode': self.episode,
                'season': self.season
            })

        return json.dumps(return_value)