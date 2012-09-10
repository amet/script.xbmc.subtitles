# -*- coding: utf-8 -*- 

import os
import sys
import xbmc
import urllib
import struct
import xbmcvfs
import xmlrpclib

__scriptname__ = sys.modules[ "__main__" ].__scriptname__

BASE_URL_XMLRPC = u"http://api.opensubtitles.org/xml-rpc"


class OSDBServer:

  def mergesubtitles( self ):
    self.subtitles_list = []
    if( len ( self.subtitles_hash_list ) > 0 ):
      for item in self.subtitles_hash_list:
        if item["format"].find( "srt" ) == 0 or item["format"].find( "sub" ) == 0:
          self.subtitles_list.append( item )

    if( len ( self.subtitles_list ) > 0 ):
      self.subtitles_list.sort(key=lambda x: [not x['sync'],x['lang_index']])

  def searchsubtitles( self, srch_string, languages, hash_search, _hash = "000000000", size = "000000000"):
    msg                      = ""
    lang_index               = 3
    searchlist               = []
    self.subtitles_hash_list = []
  
    self.server = xmlrpclib.Server( BASE_URL_XMLRPC, verbose=0 )
    login = self.server.LogIn("", "", "en", "XBMC_Subtitles")
  
    self.osdb_token  = login[ "token" ]
    log( __name__ ,"Token:[%s]" % str(self.osdb_token))
  
    try:
      if ( self.osdb_token ) :
        if hash_search:
          searchlist.append({'sublanguageid':','.join(languages), 'moviehash':_hash, 'moviebytesize':str( size ) })
        searchlist.append({'sublanguageid':','.join(languages), 'query':srch_string })
        search = self.server.SearchSubtitles( self.osdb_token, searchlist )
        if search["data"]:
          for item in search["data"]:
            if item["ISO639"]:
              lang_index=0
              for user_lang_id in languages:
                if user_lang_id == item["ISO639"]:
                  break
                lang_index+=1
              flag_image = "flags/%s.gif" % item["ISO639"]
            else:                                
              flag_image = "-.gif"

            if str(item["MatchedBy"]) == "moviehash":
              sync = True
            else:                                
              sync = False

            self.subtitles_hash_list.append({'lang_index'    : lang_index,
                                             'filename'      : item["SubFileName"],
                                             'link'          : item["ZipDownloadLink"],
                                             'language_name' : item["LanguageName"],
                                             'language_flag' : flag_image,
                                             'language_id'   : item["SubLanguageID"],
                                             'ID'            : item["IDSubtitle"],
                                             'rating'        : str(int(item["SubRating"][0])),
                                             'format'        : item["SubFormat"],
                                             'sync'          : sync,
                                             'hearing_imp'   : int(item["SubHearingImpaired"]) != 0
                                             })
            
    except:
      msg = "Error Searching For Subs"
    
    self.mergesubtitles()
    return self.subtitles_list, msg


def log(module,msg):
  xbmc.log((u"### [%s] - %s" % (module,msg,)).encode('utf-8'),level=xbmc.LOGDEBUG ) 

def hashFile(file_path):
    longlongformat = 'q'  # long long
    bytesize = struct.calcsize(longlongformat)
    f = xbmcvfs.File(file_path)
    
    filesize = f.size()
    hash = filesize
    
    if filesize < 65536 * 2:
        return "SizeError"
    
    buffer = f.read(65536)
    f.seek(max(0,filesize-65536),0)
    buffer += f.read(65536)
    f.close()
    for x in range((65536/bytesize)*2):
        size = x*bytesize
        (l_value,)= struct.unpack(longlongformat, buffer[size:size+bytesize])
        hash += l_value
        hash = hash & 0xFFFFFFFFFFFFFFFF
    
    returnHash = "%016x" % hash
    return filesize,returnHash

def search_subtitles( item ):
  ok = False
  hash_search = False
  if len(item['tvshow']) > 0:                                            # TvShow
    OS_search_string = ("%s S%.2dE%.2d" % (item['tvshow'],
                                           int(item['season']),
                                           int(item['episode']),)
                                          ).replace(" ","+")      
  else:
    if str(item['year']) == "":
      item['title'], item['year'] = xbmc.getCleanMovieTitle( item['title'] )

    OS_search_string = item['title'].replace(" ","+")
    
  log( __name__ , "Search String [ %s ]" % (OS_search_string,))     
 
  if item['temp'] : 
    hash_search = False
    file_size   = "000000000"
    SubHash     = "000000000000"
  else:
    try:
      file_size, SubHash   = hashFile(item['file_original_path'])
      log( __name__ ,"xbmc module hash and size")
      hash_search = True
    except:  
      file_size   = ""
      SubHash     = ""
      hash_search = False
  
  if file_size != "" and SubHash != "":
    log( __name__ ,"File Size [%s]" % file_size )
    log( __name__ ,"File Hash [%s]" % SubHash)
  
  log( __name__ ,"Search by hash and name %s" % (os.path.basename( item['file_original_path'] ),))
  item['subtitles_list'], item['msg'] = OSDBServer().searchsubtitles( OS_search_string, item['3let_language'], hash_search, SubHash, file_size  )

  return item


def download_subtitles (item):
  
  f = urllib.urlopen(item['subtitles_list'][item['pos']][ "link" ])
  local_file = open(item['zip_subs'], "w" + "b")

  local_file.write(f.read())
  local_file.close()
  
  item['zipped'] = True
  item['language'] = item['subtitles_list'][item['pos']][ "language_name" ]
  
  return item    
    
    
    
