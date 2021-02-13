# -*- coding: utf-8 -*-
# Module: default
# Author: 0fabris
# Created on: 01.2020
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
import os
from urllib import urlencode
import sys
import json

from DiscoveryUtils import *

#Kodi Specific Imports
import inputstreamhelper
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmc


#DRM Consts
PROTOCOL = 'mpd'
DRM = 'com.widevine.alpha'

DISC_UTILS = DiscoveryUtils()

def get_videos():
    """
    Generator function made to display different streams in Kodi UI, Kodi format
    """
    for c in DISC_UTILS.getChannels():
        try:
            if c["attributes"]["hasLiveStream"] and c["attributes"]["packages"][0] == "Free":
                yield {
                    'name' : c["attributes"]["name"],
                    'thumb': None,
                    'video': c["id"],
                    'genre': 'Live'
                }
        except:
            pass

def get_video(chan):
    """
    Function that returns the ListItem that could be played from Kodi's internal player, given channelId
    """
    links = DISC_UTILS.getMediaLinks('channel',chan)
    chheaders = urlencode({
            'User-Agent' : 'Mozilla/5.0',
            'Conax-Custom-Data': '{"Version":"1.0.0","CxAuthenticationDataToken":"%s","CxClientInfo":{"DeviceType":"Browser","DrmClientType":"Widevine-HTML5","DrmClientVersion":"1.0.0","CxDeviceId":""}}' % links['protection']['drmToken'],
            'preauthorization': links['protection']['drmToken'],
            'Origin':'https://www.discoveryplus.it'
        })
    
    ishelper = inputstreamhelper.Helper(PROTOCOL, drm=DRM)
    if ishelper.check_inputstream():
        listitem = xbmcgui.ListItem()
        listitem.setPath(links['streaming']['dash']['url'])
        listitem.setProperty("inputstreamaddon", ishelper.inputstream_addon)
        listitem.setProperty("inputstream.adaptive.manifest_type", PROTOCOL)
        listitem.setProperty("inputstream.adaptive.license_type", DRM)
        listitem.setProperty("inputstream.adaptive.license_key", "%s|%s|R{SSM}|"% (links['protection']['schemes']['widevine']['licenseUrl'],chheaders))
        return listitem
    return None
