# -*- coding: utf-8 -*-
# Module: default
# Author: 0fabris
# Created on: 02.2020
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import requests
import os
from hashlib import sha256
import time
from urllib import urlencode
import sys
import json
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmc

#DiscoveryUtils Class
class DiscoveryUtils:
    
    APIURL = "https://disco-api.discoveryplus.it"

    #Constructor
    def __init__(self):
        self.cooks = self.getCookies()
        self.headers = {
            'User-Agent' : 'Mozilla/5.0',
            'Origin': 'https://www.discoveryplus.it',
            'X-disco-client': 'WEB:UNKNOWN:discoveryplus-player:acc9abff4',
            'Cookie': self.cooks,
        }

    #private functions

    def __APIGET(self,url):
        r = requests.get(DiscoveryUtils.APIURL + url, headers=self.headers)
        #self.log(DiscoveryUtils.APIURL + url)
        #self.log(r.text)
        return r.json()

    #methods
    def getCookies(self):
        path = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('profile').decode('utf-8'))
        
        if not os.path.exists(path):
            os.mkdir(path)
        if ('cooks' in os.listdir(path)):
            with open(path+'/cooks','r') as f:
                cooks = f.read()
        else:
            #Cookie generation with random sha256 time based deviceId
            #TODO Add check if cookie expired
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


    #Log function in file
    def log(self,msg):
        with open(xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('profile').decode('utf-8'))+"/test",'a+') as f:
            f.write("[" + str(time.time())+ "] " + msg + "\n")

    #methods used to call API
    def getShows(self):
        return self.__APIGET("/cms/routes/programmi?decorators=viewingHistory&include=default")['included']

    def getChannels(self):
        return self.__APIGET("/cms/routes/canali?decorators=viewingHistory&include=default")['included']

    def getMediaLinks(self,rtype,chanid):
        return self.__APIGET('/playback/v2/{}PlaybackInfo/{}?usePreAuth=true'.format(rtype,chanid))['data']['attributes']
    
    def getSerie(self, path):
        return self.__APIGET('/cms/routes' + path +"?decorators=viewingHistory&include=default")['included']

    def getSeason(self,path,ns):
        return self.__APIGET('/cms/collections/'+path+"?decorators=viewingHistory&include=default&" + ns)['included']
