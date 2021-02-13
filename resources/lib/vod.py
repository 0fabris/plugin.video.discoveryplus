# -*- coding: utf-8 -*-
# Module: default
# Author: 0fabris
# Created on: 01.2020
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

#Kodi Specific Imports
import inputstreamhelper
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmc

from DiscoveryUtils import *

DISC_UTILS = DiscoveryUtils()


#DRM Consts
PROTOCOL = 'mpd'
DRM = 'com.widevine.alpha'

def serie_episodes(s_path):
    '''
    Function that gets every episode of every season of given program
    '''
    for i in DISC_UTILS.getSerie(s_path): #prendo la serie
        if i['type'] == 'collection' and 'seasongrid' in i['attributes']['alias']:
            idp = i['id']
            for x in i['attributes']['component']['filters'][0]['options']:
                try:
                    for z in (DISC_UTILS.getSeason(idp,x['parameter']+ "&" + i['attributes']['component']['mandatoryParams'])):
                        if z['type'] == 'video':
                            yield {
                                'name' : "Stagione " + str(z['attributes']['seasonNumber']) +" - "+z['attributes']["name"],
                                'thumb': None,
                                'video': z["id"],
                                'genre': 'VOD'
                            }
                except:
                    break

def get_videos():
    '''
    Function that gets a list of VOD Contents
    '''
    routes = {}
    for i in DISC_UTILS.getShows():
        if i['type'] == 'route':
            routes[i['id']] = i['attributes']['url']
        if i['type'] == 'show' and i['relationships']['contentPackages']['data'][0]['id'] == 'Free':
            yield {
                'name' : i['attributes']['name'],
                'thumb': None,
                'path': routes[i['relationships']['routes']['data'][0]['id']],
                'genre': 'VOD',
                'series': i['attributes']['seasonNumbers'],
            }
            
def get_video(idv):
    """
    Function that returns the ListItem that could be played from Kodi's internal player, given channelId
    """
    links = DISC_UTILS.getMediaLinks('video',idv)
    DISC_UTILS.log(str(links))
    
    ishelper = inputstreamhelper.Helper(PROTOCOL, drm=DRM)
    
    listitem = xbmcgui.ListItem()

    #se non c'e DRM faccio partire link m3u8
    if not links['protection']['drmEnabled']:
        listitem.setPath(links['streaming']['hls']['url'])
        return listitem
    
    listitem.setPath(links['streaming']['dash']['url'])

    if ishelper.check_inputstream():
        chheaders = urlencode({
            'User-Agent' : 'Mozilla/5.0',
            'Conax-Custom-Data': '{"Version":"1.0.0","CxAuthenticationDataToken":"%s","CxClientInfo":{"DeviceType":"Browser","DrmClientType":"Widevine-HTML5","DrmClientVersion":"1.0.0","CxDeviceId":""}}' % links['protection']['drmToken'],
            'preauthorization': links['protection']['drmToken'],
            'Origin':'https://www.discoveryplus.it'
        })

        listitem.setProperty("inputstreamaddon", ishelper.inputstream_addon)
        listitem.setProperty("inputstream.adaptive.manifest_type", PROTOCOL)
        listitem.setProperty("inputstream.adaptive.license_type", DRM)
        listitem.setProperty("inputstream.adaptive.license_key", "%s|%s|R{SSM}|"% (links['protection']['schemes']['widevine']['licenseUrl'],chheaders))
    return listitem
