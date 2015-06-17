import threading
import time
import uuid
from services import config
from services.logging import log
import xbmc
import xbmcgui

__author__ = 'Mathieu'


class Dialog(object):
    # Position & sizes of dialog elements
    DEFAULT_DIALOG_HEIGHT = 64
    DEFAULT_POSITION_USER_PROFILE_IMAGE = {
        'x': 8,
        'y': 8,
        'width': 48,
        'height': 48
    }
    DEFAULT_POSITION_CONTENT = {
        'x': 64,
        'y': 0,
        'width': 720,
        'height': 400
    }
    DEFAULT_POSITION_USERNAME_AND_DATE = {
        'x': 64,
        'y': 24,
        'width': 720,
        'height': 400
    }

    def __init__(self, tweet, index):
        self.tweet = tweet
        if index < 1 or not isinstance(index, int):
            raise (AttributeError, "Dialog index must be int and cannot be lower than 0.")
        self.index = index
        self.creation_time = time.time()
        self.uuid = uuid.uuid4()
        self.controls = []
        self.controls_data = self.create_controls_data(self.tweet.status)

    def create_controls_data(self, status):
        log("Dialog {uuid}: creating".format(uuid=self.uuid))
        log("Dialog {uuid} user_profile_image: {upi}".format(uuid=self.uuid, upi=status.get('user_profile_image_file')))
        log("Dialog {uuid} text {text}".format(uuid=self.uuid, text=status.get('text')))
        log("Dialog {uuid} username {un}".format(uuid=self.uuid, un=status.get('user_screen_name')))
        return {
            'user_profile_image': {
                'control_class': xbmcgui.ControlImage,
                'image': status.get('user_profile_image_file'),
                'parameters': {
                    'filename': self.tweet.status['user_profile_image_file'],
                    'aspectRatio': 2,   # 2 = black bars (http://romanvm.github.io/xbmcstubs/docs/classxbmcgui_1_1_control_image.html#acc5e48069c6528a9bcfd803578788610)
                    'x': self.DEFAULT_POSITION_USER_PROFILE_IMAGE['x'],
                    'y': self.DEFAULT_POSITION_USER_PROFILE_IMAGE['y'] + (self.DEFAULT_DIALOG_HEIGHT * (self.index-1)),
                    'width': self.DEFAULT_POSITION_USER_PROFILE_IMAGE['width'],
                    'height': self.DEFAULT_POSITION_USER_PROFILE_IMAGE['height'],
                }
            },
            'content': {
                'control_class': xbmcgui.ControlTextBox,
                'text': status.get('text'),
                'parameters': {
                    'x': self.DEFAULT_POSITION_CONTENT['x'],
                    'y': self.DEFAULT_POSITION_CONTENT['y'] + (self.DEFAULT_DIALOG_HEIGHT * (self.index-1)),
                    'width': self.DEFAULT_POSITION_CONTENT['width'],
                    'height': self.DEFAULT_POSITION_CONTENT['height'],
                    'font': 'font13',
                    'textColor': '0xFFFFFFFF',
                }
            },
            'username': {
                'control_class': xbmcgui.ControlTextBox,
                'text': status.get('user_screen_name'),
                'parameters': {
                    'x': self.DEFAULT_POSITION_USERNAME_AND_DATE['x'],
                    'y': self.DEFAULT_POSITION_USERNAME_AND_DATE['y'] + (self.DEFAULT_DIALOG_HEIGHT * (self.index-1)),
                    'width': self.DEFAULT_POSITION_USERNAME_AND_DATE['width'],
                    'height': self.DEFAULT_POSITION_USERNAME_AND_DATE['height'],
                    'font': 'font10',
                    'textColor': '0xFFCCCCCC'
                }
            }
        }

    def add_controls_to_window(self, window):
        for key, data in self.controls_data.items():
            log('Dialog {uuid}: adding control "{key}"'.format(uuid=self.uuid, key=key))
            log('Dialog {uuid} coordinates for {key} are x: {x}, y:{y}, w:{w}, h:{h}'.format(
                key=key,
                uuid=self.uuid,
                x=data.get('parameters').get('x'),
                y=data.get('parameters').get('y'),
                w=data.get('parameters').get('width'),
                h=data.get('parameters').get('height')
            ))
            control = data.get('control_class')(**data.get('parameters'))
            self.controls.append(control)
            window.addControl(control)
            # Spent TWO NIGHTS FIGURING THIS OUT: setText() AFTER the control has been added to the window
            # AFTER!
            # RAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHHHHH
            if data.get('text', None):
                try:
                    log("Dialog {uuid}: adding text '{text}'".format(uuid=self.uuid, text=data.get('text')))
                    control.setText(data.get('text'))
                except AttributeError, e:
                    log(str(e))
            if data.get('image', None):
                try:
                    log("Dialog {uuid}: adding image '{image}'".format(uuid=self.uuid, image=data.get('image')))
                    control.setImage(data.get('image', None))
                except AttributeError, e:
                    log(str(e))
            control.setVisible(1)

    def show(self):
        def show_dialog():        # Do this asynchronously
            window = xbmcgui.Window(xbmcgui.getCurrentWindowId())
            self.add_controls_to_window(window)
            log("Dialog {uuid}: showing '{text}' by @{username}".format(
                uuid=self.uuid,
                text=self.controls_data.get('content').get('text'),
                username=self.controls_data.get('username').get('text')
                ))
            # Wait for 3 seconds & then close
            xbmc.sleep(config.DIALOG_LIFESPAN_MS)
            log("Dialog {uuid}: lifespan reached.".format(uuid=self.uuid))
            for control in self.controls:
                log("Dialog {uuid}: removing control {ctrl}".format(uuid=self.uuid, ctrl=control))
                window.removeControl(control)

        t = threading.Thread(target=show_dialog, args=())
        t.start()