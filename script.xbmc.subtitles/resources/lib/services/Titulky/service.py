
################################   Sublight.si #################################


import sys
import os
import xmlrpclib
from utilities import  toOpenSubtitles_two
import md5
import time
import array
import httplib
import xbmc
import xml.dom.minidom
import xml.sax.saxutils as SaxUtils
import base64
import gui

_ = sys.modules[ "__main__" ].__language__
__scriptname__ = sys.modules[ "__main__" ].__scriptname__


def search_subtitles( file_original_path, title, tvshow, year, season, episode, set_temp, rar, lang1, lang2, lang3 ): #standard input
    print 'path '+file_original_path
    print 'title '+title
    print 'tvshow '+tvshow
    print 'year '+year
    print 'season '+season
    print 'episode'+episode
    print 'set_temp '+str(set_temp)
    print 'rar '+str(rar)
    print 'lang1 '+lang1
    print 'lang2 '+lang2
    print 'lang3 '+lang3
    session_id = "000000000000000022020"
    subtitles_list = []      
    subtitles_list.append( { "title" : 'titulek', "year" : '2010', "filename" : 'soubor.srt', "language_name" : 'Czech', "ID" : 'ID', "mediaType" : 'mediaType', "numberOfDiscs" : '2', "downloads" : 'downloads', "sync" : True, "rating" :'10', "language_flag":'image.jpg' } )            
    subtitles_list.append( { "title" : 'titulek', "year" : '2010', "filename" : 'soubor2.srt', "language_name" : 'Czech', "ID" : 'ID', "mediaType" : 'mediaType', "numberOfDiscs" : '1', "downloads" : 'downloads', "sync" : False, "rating" :'10', "language_flag":'image.jpg' } )                
    return subtitles_list, session_id, ""  #standard output



def download_subtitles (subtitles_list, pos, zip_subs, tmp_sub_dir, sub_folder, session_id): #standard input


    subtitle_id   =                          subtitles_list[pos][ "ID" ]
    language      =                          subtitles_list[pos][ "language_name" ]

    print subtitles_list
    print pos
    print zip_subs
    print tmp_sub_dir
    print sub_folder
    print session_id
    print subtitle_id
    print language
    return True,language, "" #standard output
