# -*- coding: utf-8 -*-
# Module: default
# Author: 0fabris
# Created on: 01.2020
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import sys
from urllib import urlencode
from urlparse import parse_qsl
import xbmcaddon
import xbmcgui
import xbmcplugin
import importlib

# Get the plugin url in plugin:// notation.
_url = sys.argv[0]
# Get the plugin handle as an integer number.
_handle = int(sys.argv[1])

CATEGORIES = {
    'Live': ['resources.lib.live',""],
    'VOD Contents':['resources.lib.vod',""]
}

def get_url(**kwargs):
    """
    Create a URL for calling the plugin recursively from the given set of keyword arguments.

    :param kwargs: "argument=value" pairs
    :type kwargs: dict
    :return: plugin call URL
    :rtype: str
    """
    return '{0}?{1}'.format(_url, urlencode(kwargs))


def get_categories():
    """
    Get the list of video categories.

    Here you can insert some parsing code that retrieves
    the list of video categories (e.g. 'Movies', 'TV-shows', 'Documentaries' etc.)
    from some site or server.

    .. note:: Consider using `generator functions <https://wiki.python.org/moin/Generators>`_
        instead of returning lists.

    :return: The list of video categories
    :rtype: types.GeneratorType
    """
    return CATEGORIES.iterkeys()


def get_videos(category):
    """
    Get the list of videofiles/streams.

    Here you can insert some parsing code that retrieves
    the list of video streams in the given category from some site or server.

    .. note:: Consider using `generators functions <https://wiki.python.org/moin/Generators>`_
        instead of returning lists.

    :param category: Category name
    :type category: str
    :return: the list of videos in the category
    :rtype: list
    """

    l = importlib.import_module(category)
    return l.get_videos() 


def list_categories():
    """
    Create the list of video categories in the Kodi interface.
    """
    xbmcplugin.setPluginCategory(_handle, 'Discovery+')
    xbmcplugin.setContent(_handle, 'videos')
    categories = get_categories()

    for category in categories:
        list_item = xbmcgui.ListItem(label=category)
        list_item.setInfo('video', {'title': category,
                                    'genre': category,
                                    'mediatype': 'video'})
        url = get_url(action="list",lib=CATEGORIES[category][0])
        is_folder = True
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.endOfDirectory(_handle)


def list_videos(category):
    """
    Create the list of playable videos in the Kodi interface.

    :param category: Category name
    :type category: str
    """
    xbmcplugin.setContent(_handle, 'videos')
    videos = get_videos(category)
    for video in videos:
        list_item = xbmcgui.ListItem(label=video['name'])
        list_item.setInfo('video', {'title': video['name'],
                                    'genre': video['genre'],
                                    'mediatype': 'video'})

        list_item.setProperty('IsPlayable', 'true')
        
        url = get_url(action='play', lib=category, stream_id=video["video"])
        
        is_folder = False
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.endOfDirectory(_handle)


def play_video(lib, s_id):
    """
    Play a video by the provided path.

    :param path: Fully-qualified video URL
    :type path: str
    """

    l = importlib.import_module(lib)
    xbmcplugin.setResolvedUrl(_handle, True, listitem=l.get_channel(s_id))


def router(paramstring):
    """
    Router function that calls other functions
    depending on the provided paramstring

    :param paramstring: URL encoded plugin paramstring
    :type paramstring: str
    """
    params = dict(parse_qsl(paramstring))
    if params:
        if params['action'] == 'list':
            list_videos(params['lib'])
        elif params['action'] == 'play':
            play_video(params["lib"],params['stream_id'])
        else:
            raise ValueError('Invalid paramstring: {0}!'.format(paramstring))
    else:
        list_categories()


if __name__ == '__main__':
    router(sys.argv[2][1:])
