import json
from services.config import KODI_URL, KODI_AUTH, KODI_JSONRPC_BASE_PAYLOAD
from services.logging import log
import xbmc


def internal_jsonrpc_call(method="", params=None):
    payload = KODI_JSONRPC_BASE_PAYLOAD.copy()
    payload.update({"method": method})
    if params:
        payload.update({"params": params})

    log("Executing {call}".format(call=json.dumps(payload)))
    return_value = xbmc.executeJSONRPC(json.dumps(payload))
    log("Received {result}".format(result=json.loads(return_value)))
    return json.loads(return_value).get('result', None)


def get_video_player_id():
    # Check if anything is playing
    players = None
    try:
        players = internal_jsonrpc_call(method="Player.GetActivePlayers")
    except Exception, e:
        log("Error while getting players")
        log(e)

    if players:
        pid = None
        for player in players:
            if player.get('type') == 'video':
                log("Video player {player} found.".format(player=player))
                pid = player.get('playerid')
                log("Player %i is playing video." % pid)
                return pid
    else:
        log("No active player(s) found.")


def get_timestamp(player_id):
    position = internal_jsonrpc_call(
        method="Player.GetProperties",
        params={"playerid": player_id, "properties": ["position", "percentage", "time"]}
    )
    return position.get('time')


def get_item_info(player_id):
    item_playing = internal_jsonrpc_call(
        method="Player.GetItem",
        params={
            "playerid": player_id,
            "properties": ["title",
                           "file",
                           "season",
                           "episode",
                           "showtitle",
                           "imdbnumber"]
        }
    )

    if "error" in item_playing:  # Sanity check
        log("Nothing is playing right now.")
        return None
    else:
        return item_playing.get('item')

def get_screenshot():
    # Check this if screenshots are black
    # http://forum.kodi.tv/showthread.php?tid=193294&pid=1694041#pid1694041
    capture = xbmc.RenderCapture()
    capture.capture(1920, 1080)
    capture.waitForCaptureStateChangeEvent(500)  # Wait x milliseconds
    size = (capture.getWidth(), capture.getHeight())
    log("Captured image.")
    log("Size:\t%i, %i" % (size[0], size[1]))
    log("Format:\t%s" % capture.getImageFormat())
    return capture.getImage() if capture.getCaptureState() == xbmc.CAPTURE_STATE_DONE else None