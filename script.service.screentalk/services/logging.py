import xbmc
# from config import SCRIPTNAME
SCRIPTNAME = "ScreenTalk"

def log(msg):
    global SCRIPTNAME
    xbmc.log("%s: %s" % (SCRIPTNAME, msg))

