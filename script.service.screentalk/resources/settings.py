import xbmc
import xbmcaddon

__author__ = 'Mathieu'
__addon__ = xbmcaddon.Addon()
__addonname__ = __addon__.getAddonInfo('id')
__addonversion__ = __addon__.getAddonInfo('version')
__addonpath__ = __addon__.getAddonInfo('path').decode('utf-8')
__addonicon__ = xbmc.translatePath('%s/icon.png' % __addonpath__)
__language__ = __addon__.getLocalizedString
_addon = xbmcaddon.Addon(id=__addonname__)


def get_setting(setting_id):
    addon = xbmcaddon.Addon(id=__addonname__)
    return addon.getSetting(setting_id)