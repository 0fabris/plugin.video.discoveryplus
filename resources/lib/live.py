import requests
import os
from hashlib import sha256
import time
from urllib import urlencode
import sys
import json
import inputstreamhelper
import xbmcaddon
import xbmcgui
import xbmcplugin

#DRM
PROTOCOL = 'mpd'
DRM = 'com.widevine.alpha'


def getCookies():
    path = xbmcaddon.Addon().getAddonInfo('path').decode('utf-8')
    print(path)
    if os.path.exists(path) and ('cooks' in os.listdir(path)):
        with open(path+'/cooks','r') as f:
            cooks = f.read()
    else:
        tokurl = "https://disco-api.discoveryplus.it/token?" + urlencode({
            'realm' : 'dplayit',
            'deviceId': sha256(str(time.time()).encode('utf-8')).hexdigest(),
            'shortlived':True
        })
        
        headers = {
            'User-Agent' : 'Mozilla/5.0',
            'Origin': 'https://www.discoveryplus.it',
            'X-disco-client': 'WEB:UNKNOWN:dplay-client:2.6.0',
            'X-disco-params': 'realm=dplayit'
        }
        
        r = requests.get(tokurl,headers=headers)
        with open(path+'/cooks','w') as f:
            cooks = r.headers['set-cookie'].split(' ')[0]
            f.write(cooks)

    return cooks

def getChannels():
    headers = {
        'User-Agent' : 'Mozilla/5.0',
        'Origin': 'https://www.discoveryplus.it',
        'X-disco-client': 'WEB:UNKNOWN:discoveryplus-player:acc9abff4',
        'Cookie': getCookies(),
    }
    chanurl = "https://disco-api.discoveryplus.it/cms/routes/canali?decorators=viewingHistory&include=default"
    r = requests.get(chanurl,headers=headers).json()
    return r['included']

def getLinks(chanid):
    headers = {
        'User-Agent' : 'Mozilla/5.0',
        'Origin': 'https://www.discoveryplus.it',
        'X-disco-client': 'WEB:UNKNOWN:discoveryplus-player:acc9abff4',
        'Cookie': getCookies(),
    }
    url = 'https://disco-api.discoveryplus.it/playback/v2/channelPlaybackInfo/{}?usePreAuth=true'.format(chanid)
    r = requests.get(url,headers=headers).json()
    return r['data']['attributes']

def get_videos():
    for c in getChannels():
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

def get_channel(chan):
    links = getLinks(chan)
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
        #xbmcplugin.setResolvedUrl(handle, True, listitem)
        return listitem
    return None