
################################   Titulky.com #################################


import sys
import os
import xmlrpclib

import time
import array
import urllib2,urllib,re,cookielib

#_ = sys.modules[ "__main__" ].__language__
#__scriptname__ = sys.modules[ "__main__" ].__scriptname__

"""
            <tr class="row2">
                    <td><a href="Pulp-Fiction-118518.htm" >Pulp Fiction</a></td>
          <td align="center"><a class="fixedTip" title="Pulp.Fiction.1994.720p.BluRay.x264-SiNNERS"><img src="img/ico/rel.gif" atl="release"/></a></td>        
          <td>&nbsp;</td>
          <td>1994</td>
                    <td>18.11.2008</td>        
          <td align="right">681</td>
          <td>CZ</td>
          <td>1</td>
          <td align="right">8138.46MB</td>
                    <td>
                           <a href="" onclick="UD('119203');return false;" > aAaX</a>
                      </td>
        </tr>

"""

subtitle_pattern='..<tr class=\"row[12]\">\s+?<td?[= \w\"]+><a href=\"[\w-]+-(?P<id>\d+).htm\"[ ]?>(?P<title>[\w ]*)</a></td>\s+?<td?[= \w\"]+>(<a?[= \w\"]+title=\"(?P<sync>[\w.\d \(\)\]\[-]+)\"><img?[= \w\\./"]+></a>)?</td>\s+?<td?[= \w\"]+>(?P<tvshow>[\w\;\&]+)</td>\s+<td?[= \w\"]+>(?P<year>\d+)</td>\s+<td?[= \w\"]+>[\w\;\&\.\d]+</td>\s+<td?[= \w\"]+>(?P<downloads>\d+)</td>\s+<td?[= \w\"]+>(?P<lang>\w{2})</td>'

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
    
class TitulkyClient(object):
	def __init__(self):
		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar()))
		opener.version = 'User-Agent=Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3 ( .NET CLR 3.5.30729)'
		urllib2.install_opener(opener)
	
	def search_subtitles(self, file_original_path, title, tvshow, year, season, episode, set_temp, rar, lang1, lang2, lang3 ):
		url = 'http://www.titulky.com?'+urllib.urlencode({'Fulltext':title,'FindUser':''})
		req = urllib2.Request(url)
		response = urllib2.urlopen(req)
		content = response.read()
		response.close()
		subtitles_list = []
		for matches in re.finditer(subtitle_pattern, content, re.IGNORECASE | re.DOTALL):
			print matches.group('id') +' ' +matches.group('title')+' '+ str(matches.group('sync'))+' '+ matches.group('tvshow')+' '+ matches.group('year')+' '+ matches.group('downloads')+' '+ matches.group('lang')
			
#client = TitulkyClient()
#client.search_subtitles('','Pulp Fiction','','','','','','','','','')
