
################################   Titulky.com #################################


import sys
import os
import xbmc

import time,calendar
import array
import urllib2,urllib,re,cookielib

_ = sys.modules[ "__main__" ].__language__
__scriptname__ = sys.modules[ "__main__" ].__scriptname__

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

subtitle_pattern='..<tr class=\"row[12]\">\s+?<td?[= \w\"]+><a href=\"[\w-]+-(?P<id>\d+).htm\"[ ]?>(?P<title>[\w\- ]*)</a></td>\s+?<td?[= \w\"]+>(<a?[= \w\"]+title=\"(?P<sync>[,\{\}\w.\d \(\)\]\[-]+)\"><img?[= \w\\./"]+></a>)?</td>\s+?<td?[= \w\"]+>(?P<tvshow>[\w\;\&]+)</td>\s+<td?[= \w\"]+>(?P<year>\d+)</td>\s+<td?[= \w\"]+>[\w\;\&\.\d]+</td>\s+<td?[= \w\"]+>(?P<downloads>\d+)</td>\s+<td?[= \w\"]+>(?P<lang>\w{2})</td>'

control_image_pattern='(secode.php\?[\w\d=]+)'

countdown_pattern='CountDown\((\d+)\)'

"""
<a rel="nofollow" id="downlink" href="/idown.php?id=48504441">www.titulky.com/idown.php?id=48504441</a>
"""

sublink_pattern='<a?[= \w\"]+href="([\w\.\?\d=/]+)\"'
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
    session_id = "0"
    client = TitulkyClient()
    
    subtitles_list = client.search_subtitles( file_original_path, title, tvshow, year, season, episode, set_temp, rar, lang1, lang2, lang3 )   
    return subtitles_list, session_id, ""  #standard output



def download_subtitles (subtitles_list, pos, zip_subs, tmp_sub_dir, sub_folder, session_id): #standard input

    subtitle_id =  subtitles_list[pos][ 'ID' ]
    print pos
    print zip_subs
    print tmp_sub_dir
    print sub_folder
    print session_id
    print subtitle_id
    icon =  os.path.join(os.getcwd(),'icon.png')
    client = TitulkyClient()
    content = client.get_subtitle_page(subtitle_id)
    control_img = client.get_control_image(content)
    if not control_img == None:
		# subtitle limit was reached .. we need to ask user to rewrite image code :(
		img = client.get_file(control_img)
		img_file = open(tmp_sub_dir+'/image.png','w')
		img_file.write(img)
		img_file.close()
    if None == None:
		print 'error !!!'
		return 
    delay = wait_time
    for i in range(wait_time+1):
		line2 = "download will start in %i seconds" % (delay,)
		xbmc.executebuiltin("XBMC.Notification(%s,%s,1000,%s)" % (__scriptname__,line2,icon))
		delay -= 1
		time.sleep(1)
    zip_file = open(zip_subs,'wb')
    data = client.get_file(link)
    print data
    zip_file.write(data)
    zip_file.close()
    return True,subtitles_list[pos]['language_name'], "" #standard output

def lang_titulky2xbmclang(lang):
	if lang == 'CZ': return 'Czech'
	if lang == 'SK': return 'Slovak'
	return 'English'

def lang2_opensubtitles(lang):
	lang = lang_titulky2xbmclang(lang)
	from utilities import  toOpenSubtitles_two
	return toOpenSubtitles_two(lang)
#	return 'cs'	    
class TitulkyClient(object):
	
	def __init__(self):
		self.server_url = 'http://titulky.com'
		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar()))
		opener.version = 'User-Agent=Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3 ( .NET CLR 3.5.30729)'
		urllib2.install_opener(opener)
	
	def search_subtitles(self, file_original_path, title, tvshow, year, season, episode, set_temp, rar, lang1, lang2, lang3 ):
		url = self.server_url+'/index.php?'+urllib.urlencode({'Fulltext':title,'FindUser':''})
		req = urllib2.Request(url)
		print 'opening url '+url
		response = urllib2.urlopen(req)
		content = response.read()
		response.close()
		subtitles_list = []
		for matches in re.finditer(subtitle_pattern, content, re.IGNORECASE | re.DOTALL):
			print matches.group('id') +' ' +matches.group('title')+' '+ str(matches.group('sync'))+' '+ matches.group('tvshow')+' '+ matches.group('year')+' '+ matches.group('downloads')+' '+ matches.group('lang')			
			file_name = matches.group('sync')
			if file_name == None: # if no sync info is found, just use title instead of None
				file_name = matches.group('title') 
			flag_image = "flags/%s.gif" % (lang2_opensubtitles(matches.group('lang')))
			subtitles_list.append( { 'title' : matches.group('title'), 'year' : matches.group('year'), "filename" : file_name, 'language_name' : lang_titulky2xbmclang(matches.group('lang')), 'ID' : matches.group('id'), "mediaType" : 'mediaType', "numberOfDiscs" : '2', "downloads" : matches.group('downloads'), "sync" : False, "rating" :'0', "language_flag":flag_image } )
		return subtitles_list
	
	def get_waittime(self,content):
		for matches in re.finditer(countdown_pattern, content, re.IGNORECASE | re.DOTALL):
			return int(matches.group(1))

	def get_link(self,content):
		for matches in re.finditer(sublink_pattern, content, re.IGNORECASE | re.DOTALL):
			return str(matches.group(1))				

	def get_control_image(self,content):
		for matches in re.finditer(control_image_pattern, content, re.IGNORECASE | re.DOTALL):
			return '/'+str(matches.group(1))
		return None

	def get_file(self,link):
		url = self.server_url+link
		print 'getting file ' + url
		req = urllib2.Request(url)
		response = urllib2.urlopen(req)
		content = response.read()
		print 'got it'
		response.close()
		return content


	def get_subtitle_page(self,id):
		timestamp = str(time.gmtime())
		url = self.server_url+'/idown.php?'+urllib.urlencode({'R':timestamp,'titulky':id,'histstamp':'','zip':'z'})
		req = urllib2.Request(url)
		print 'opening url '+url
		response = urllib2.urlopen(req)
		content = response.read()
		print 'done'
		print content
		response.close()
		return content
		

		
			
#client = TitulkyClient()
#client.search_subtitles('','Kick-Ass','','','','','','','','','')
#print client.get_subtitle_link('12576')
