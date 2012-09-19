# -*- coding: utf-8 -*- 

import os
import re
import sys
import xbmc
import shutil
import xbmcvfs
import xbmcgui
import unicodedata

_              = sys.modules[ "__main__" ].__language__
__addon__      = sys.modules[ "__main__" ].__addon__
__scriptname__ = sys.modules[ "__main__" ].__scriptname__
__cwd__        = sys.modules[ "__main__" ].__cwd__


STATUS_LABEL   = 100
LOADING_IMAGE  = 110
SUBTITLES_LIST = 120
SERVICES_LIST  = 150
CANCEL_DIALOG  = ( 9, 10, 92, 216, 247, 257, 275, 61467, 61448, )

SERVICE_DIR    = os.path.join(__cwd__, "resources", "lib", "services")

LANGUAGES      = (
    
    # Full Language name[0]        ISO 639-1[1]   ISO 639-2 Code[2]   Script Setting Language[3]   localized name id number[4]
    
    ("Albanian"                   ,       "sq",            "alb",                 "0",                     30201  ),
    ("Arabic"                     ,       "ar",            "ara",                 "1",                     30202  ),
    ("Belarusian"                 ,       "hy",            "arm",                 "2",                     30203  ),
    ("Bosnian"                    ,       "bs",            "bos",                 "3",                     30204  ),
    ("Bulgarian"                  ,       "bg",            "bul",                 "4",                     30205  ),
    ("Catalan"                    ,       "ca",            "cat",                 "5",                     30206  ),
    ("Chinese"                    ,       "zh",            "chi",                 "6",                     30207  ),
    ("Croatian"                   ,       "hr",            "hrv",                 "7",                     30208  ),
    ("Czech"                      ,       "cs",            "cze",                 "8",                     30209  ),
    ("Danish"                     ,       "da",            "dan",                 "9",                     30210  ),
    ("Dutch"                      ,       "nl",            "dut",                 "10",                    30211  ),
    ("English"                    ,       "en",            "eng",                 "11",                    30212  ),
    ("Estonian"                   ,       "et",            "est",                 "12",                    30213  ),
    ("Persian"                    ,       "fa",            "per",                 "13",                    30247  ),
    ("Finnish"                    ,       "fi",            "fin",                 "14",                    30214  ),
    ("French"                     ,       "fr",            "fre",                 "15",                    30215  ),
    ("German"                     ,       "de",            "ger",                 "16",                    30216  ),
    ("Greek"                      ,       "el",            "ell",                 "17",                    30217  ),
    ("Hebrew"                     ,       "he",            "heb",                 "18",                    30218  ),
    ("Hindi"                      ,       "hi",            "hin",                 "19",                    30219  ),
    ("Hungarian"                  ,       "hu",            "hun",                 "20",                    30220  ),
    ("Icelandic"                  ,       "is",            "ice",                 "21",                    30221  ),
    ("Indonesian"                 ,       "id",            "ind",                 "22",                    30222  ),
    ("Italian"                    ,       "it",            "ita",                 "23",                    30224  ),
    ("Japanese"                   ,       "ja",            "jpn",                 "24",                    30225  ),
    ("Korean"                     ,       "ko",            "kor",                 "25",                    30226  ),
    ("Latvian"                    ,       "lv",            "lav",                 "26",                    30227  ),
    ("Lithuanian"                 ,       "lt",            "lit",                 "27",                    30228  ),
    ("Macedonian"                 ,       "mk",            "mac",                 "28",                    30229  ),
    ("Norwegian"                  ,       "no",            "nor",                 "29",                    30230  ),
    ("Polish"                     ,       "pl",            "pol",                 "30",                    30232  ),
    ("Portuguese"                 ,       "pt",            "por",                 "31",                    30233  ),
    ("PortugueseBrazil"           ,       "pb",            "pob",                 "32",                    30234  ),
    ("Romanian"                   ,       "ro",            "rum",                 "33",                    30235  ),
    ("Russian"                    ,       "ru",            "rus",                 "34",                    30236  ),
    ("Serbian"                    ,       "sr",            "scc",                 "35",                    30237  ),
    ("Slovak"                     ,       "sk",            "slo",                 "36",                    30238  ),
    ("Slovenian"                  ,       "sl",            "slv",                 "37",                    30239  ),
    ("Spanish"                    ,       "es",            "spa",                 "38",                    30240  ),
    ("Swedish"                    ,       "sv",            "swe",                 "39",                    30242  ),
    ("Thai"                       ,       "th",            "tha",                 "40",                    30243  ),
    ("Turkish"                    ,       "tr",            "tur",                 "41",                    30244  ),
    ("Ukrainian"                  ,       "uk",            "ukr",                 "42",                    30245  ),
    ("Vietnamese"                 ,       "vi",            "vie",                 "43",                    30246  ),
    ("BosnianLatin"               ,       "bs",            "bos",                 "100",                   30204  ),
    ("Farsi"                      ,       "fa",            "per",                 "13",                    30247  ),
    ("English (US)"               ,       "en",            "eng",                 "100",                   30212  ),
    ("English (UK)"               ,       "en",            "eng",                 "100",                   30212  ),
    ("Portuguese (Brazilian)"     ,       "pt-br",         "pob",                 "100",                   30234  ),
    ("Portuguese (Brazil)"        ,       "pb",            "pob",                 "32",                    30234  ),
    ("Portuguese-BR"              ,       "pb",            "pob",                 "32",                    30234  ),
    ("Brazilian"                  ,       "pb",            "pob",                 "32",                    30234  ),
    ("Español (Latinoamérica)"    ,       "es",            "spa",                 "100",                   30240  ),
    ("Español (España)"           ,       "es",            "spa",                 "100",                   30240  ),
    ("Spanish (Latin America)"    ,       "es",            "spa",                 "100",                   30240  ),
    ("Español"                    ,       "es",            "spa",                 "100",                   30240  ),
    ("SerbianLatin"               ,       "sr",            "scc",                 "100",                   30237  ),
    ("Spanish (Spain)"            ,       "es",            "spa",                 "100",                   30240  ),
    ("Chinese (Traditional)"      ,       "zh",            "chi",                 "100",                   30207  ),
    ("Chinese (Simplified)"       ,       "zh",            "chi",                 "100",                   30207  ) )


REGEX_EXPRESSIONS = [ '[Ss]([0-9]+)[][._-]*[Ee]([0-9]+)([^\\\\/]*)$',
                      '[\._ \-]([0-9]+)x([0-9]+)([^\\/]*)',                     # foo.1x09 
                      '[\._ \-]([0-9]+)([0-9][0-9])([\._ \-][^\\/]*)',          # foo.109
                      '([0-9]+)([0-9][0-9])([\._ \-][^\\/]*)',
                      '[\\\\/\\._ -]([0-9]+)([0-9][0-9])[^\\/]*',
                      'Season ([0-9]+) - Episode ([0-9]+)[^\\/]*',
                      '[\\\\/\\._ -][0]*([0-9]+)x[0]*([0-9]+)[^\\/]*',
                      '[[Ss]([0-9]+)\]_\[[Ee]([0-9]+)([^\\/]*)',                 #foo_[s01]_[e01]
                      '[\._ \-][Ss]([0-9]+)[\.\-]?[Ee]([0-9]+)([^\\/]*)',        #foo, s01e01, foo.s01.e01, foo.s01-e01
                      's([0-9]+)ep([0-9]+)[^\\/]*',                              #foo - s01ep03, foo - s1ep03
                      '[Ss]([0-9]+)[][ ._-]*[Ee]([0-9]+)([^\\\\/]*)$',
                      '[\\\\/\\._ \\[\\(-]([0-9]+)x([0-9]+)([^\\\\/]*)$'
                     ]

class UserNotificationNotifier:
  def __init__(self, title, initialMessage, time = -1):
    self.__title = title
    xbmc.executebuiltin((u"Notification(%s,%s,%i)" % (title, initialMessage, time)).encode('utf-8'))
    
  def update(self, message, time = -1):
    xbmc.executebuiltin((u"Notification(%s,%s,-1)" % (self.__title, message, time)).encode("utf-8"))

  def close(self, message, time = -1):
    xbmc.executebuiltin((u"Notification(%s,%s,%i)" % (self.__title, message, time)).encode("utf-8")) 

   
def log(module,msg):
  xbmc.log((u"### [%s-%s] - %s" % (__scriptname__,module,msg,)).encode('utf-8'),level=xbmc.LOGDEBUG ) 

def regex_tvshow(compare, file, sub = ""):
  sub_info = ""
  tvshow = 0
  
  for regex in REGEX_EXPRESSIONS:
    response_file = re.findall(regex, file)                  
    if len(response_file) > 0 : 
      log( __name__ , "Regex File Se: %s, Ep: %s," % (str(response_file[0][0]),str(response_file[0][1]),) )
      tvshow = 1
      if not compare :
        title = re.split(regex, file)[0]
        for char in ['[', ']', '_', '(', ')','.','-']: 
           title = title.replace(char, ' ')
        if title.endswith(" "): title = title[:-1]
        return title,response_file[0][0], response_file[0][1]
      else:
        break
  
  if (tvshow == 1):
    for regex in regex_expressions:       
      response_sub = re.findall(regex, sub)
      if len(response_sub) > 0 :
        try :
          sub_info = "Regex Subtitle Ep: %s," % (str(response_sub[0][1]),)
          if (int(response_sub[0][1]) == int(response_file[0][1])):
            return True
        except: pass      
    return False
  if compare :
    return True
  else:
    return "","",""    

def languageTranslate(lang, lang_from, lang_to):
  for x in LANGUAGES:
    if lang == x[lang_from] :
      return x[lang_to]

def pause():
  if not xbmc.getCondVisibility('Player.Paused'):
    xbmc.Player().pause()
    return True
  else:
    return False  
    
def unpause():
  if xbmc.getCondVisibility('Player.Paused'):
    xbmc.Player().pause()  

def clean_temp( item ):
  for temp_dir in [item['stream_sub_dir'],item['tmp_sub_dir']]:
    rem_files(temp_dir) 

def rem_files(directory):
  try:
    if xbmcvfs.exists(directory):
      shutil.rmtree(directory)
  except:
    pass

  os.makedirs(directory)
      
def copy_files( subtitle_file, file_path ):
  subtitle_set = False
  try:
    xbmcvfs.copy(subtitle_file, file_path)
    log( __name__ ,"vfs module copy %s -> %s" % (subtitle_file, file_path))
    subtitle_set = True
  except :
    dialog = xbmcgui.Dialog()
    selected = dialog.yesno( __scriptname__ , _( 748 ), _( 750 ),"" )
    if selected == 1:
      file_path = subtitle_file
      subtitle_set = True

  return subtitle_set, file_path

def set_languages(item):
  item['2let_language'] = []
  item['3let_language'] = []
  item['full_language']  = remove_duplicates([languageTranslate(__addon__.getSetting( "Lang01" ), 3, 0),
                                              languageTranslate(__addon__.getSetting( "Lang02" ), 3, 0),
                                              languageTranslate(__addon__.getSetting( "Lang03" ), 3, 0)])

  for language in item['full_language']:
    item['2let_language'].append(languageTranslate(language, 0, 1))
    item['3let_language'].append(languageTranslate(language, 0, 2))
 
  return item

def remove_duplicates(list):
  seen = set()
  seen_add = seen.add
  item = [ x for x in list if x not in seen and not seen_add(x)]
  return item

def get_language(lang):
  if len(lang) > 1 and len(lang) < 4:
    lang = languageTranslate(lang,len(lang)-1,0)
  return lang  

def normalize(str):
  return unicodedata.normalize(
         'NFKD', unicode(unicode(str, 'utf-8'))
         ).encode('ascii','ignore')
