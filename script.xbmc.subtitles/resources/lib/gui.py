# -*- coding: utf-8 -*-

import os
import re
import sys
import xbmc
import urllib
import socket
import xbmcgui

from utilities import *

_              = sys.modules[ "__main__" ].__language__
__scriptname__ = sys.modules[ "__main__" ].__scriptname__
__addon__      = sys.modules[ "__main__" ].__addon__
__profile__    = sys.modules[ "__main__" ].__profile__
__version__    = sys.modules[ "__main__" ].__version__

class GUI( xbmcgui.WindowXMLDialog ):
        
  def __init__( self, *args, **kwargs ):        
    pass

  def onInit( self ):
    self.on_run()

  def on_run( self ):
    if not xbmc.getCondVisibility("VideoPlayer.HasSubtitles"):
      self.getControl( 111 ).setVisible( False )
    self.list_services()
    try:
      self.Search_Subtitles()
    except:
      errno, errstr = sys.exc_info()[:2]
      xbmc.sleep(2000)
      self.close()      

  def set_allparam(self):
    self.item                   = dict()
    self.item['list']           = []
    self.item['stackPath']      = []
    self.item['man_search_str'] = ""
    self.item['temp']           = False
    self.item['rar']            = False
    self.item['stack']          = False
    self.item['autoDownload']   = False
    self.item['sub_folder']     = xbmc.translatePath(__addon__.getSetting( "subfolderpath" )).decode("utf-8")   # User specified subtitle folder
    self.item['year']           = xbmc.getInfoLabel("VideoPlayer.Year")                                         # Year  
    self.item['season']         = str(xbmc.getInfoLabel("VideoPlayer.Season"))                                  # Season
    self.item['episode']        = str(xbmc.getInfoLabel("VideoPlayer.Episode"))                                 # Episode
    self.item['mansearch']      = __addon__.getSetting( "searchstr" ) == "true"                                 # Manual search string??
    self.item['parsearch']      = __addon__.getSetting( "par_folder" ) == "true"                                # Parent folder as search string
    self.item['tmp_sub_dir']    = os.path.join( __profile__ ,"sub_tmp" )                                        # Temporary subtitle extraction directory
    self.item['stream_sub_dir'] = os.path.join( __profile__ ,"sub_stream" )


    service_list        = []
    service             = ""
    use_subs_folder     = __addon__.getSetting( "use_subs_folder" ) == "true"                                  # use 'Subs' subfolder for storing subtitles
    movieFullPath       = urllib.unquote(xbmc.Player().getPlayingFile().decode('utf-8'))                       # Full path of a playing file
    path                = __addon__.getSetting( "subfolder" ) == "true"                                        # True for movie folder
    
    clean_temp(self.item)                                                                                      # clean temp dirs
    set_languages(self.item)                                                                                   # Get all languages

    if ( movieFullPath.find("http") > -1 ):
      self.item['sub_folder'] = self.item['stream_sub_dir']
      self.item['temp'] = True

    elif ( movieFullPath.find("rar://") > -1 ):
      self.item['rar'] = True
      movieFullPath = movieFullPath[6:]
      if path:
        if use_subs_folder:
          self.item['sub_folder'] = os.path.join(os.path.dirname(os.path.dirname( movieFullPath )),'Subs')
        else:
          self.item['sub_folder'] = os.path.dirname(os.path.dirname( movieFullPath ))  
    
    elif ( movieFullPath.find("stack://") > -1 ):
      self.item['stackPath'] = movieFullPath.split(" , ")
      movieFullPath = self.item['stackPath'][0][8:]
      self.item['stack'] = True

    if not path:
      if len(self.item['sub_folder']) < 1 :
        if use_subs_folder:
          self.item['sub_folder'] = os.path.join(os.path.dirname( movieFullPath ),'Subs')
        else:
          self.item['sub_folder'] = os.path.dirname( movieFullPath )

    if path and not self.item['rar'] and not self.item['temp']:
      if use_subs_folder:
        self.item['sub_folder'] = os.path.join(os.path.dirname( movieFullPath ),'Subs')
      else:
        self.item['sub_folder'] = os.path.dirname( movieFullPath )    
      if self.item['sub_folder'].find("smb://") > -1:
        if self.item['temp']:
          dialog = xbmcgui.Dialog()
          self.item['sub_folder'] = dialog.browse( 0, _( 766 ), "files")
    
    if self.item['episode'].lower().find("s") > -1:                                 # Check if season is "Special"             
      self.item['season'] = "0"                                                     #
      self.item['episode'] = self.item['episode'][-1:]                              #

    self.item['tvshow'] = normalize(xbmc.getInfoLabel("VideoPlayer.TVshowtitle"))   # Show
    self.item['title']  = normalize(xbmc.getInfoLabel("VideoPlayer.Title"))         # Title

    if self.item['tvshow'] == "":
      if str(self.item['year']) == "":
        title, season, episode = regex_tvshow(False, self.item['title'])
        if episode != "":
          self.item['season'] = str(int(season))
          self.item['episode'] = str(int(episode))
          self.item['tvshow'] = title
        else:
          self.item['title'], self.item['year'] = xbmc.getCleanMovieTitle( self.item['title'] )
    else:
      self.item['year'] = ""

    self.item['file_original_path'] = urllib.unquote ( movieFullPath )             # Movie Path

    if (__addon__.getSetting( "fil_name" ) == "true"):                             # Display Movie name or search string
      self.item['file_name'] = os.path.basename( movieFullPath )
    else:
      if (len(str(self.item['year'])) < 1 ) :
        self.item['file_name'] = self.item['title'].encode('utf-8')
        if (len(self.item['tvshow']) > 0):
          self.item['file_name'] = "%s S%.2dE%.2d" % (self.tvshow.encode('utf-8'),
                                              int(self.item['season']),
                                              int(self.item['episode'])
                                             )
      else:
        self.item['file_name'] = "%s (%s)" % (self.item['title'].encode('utf-8'), str(self.item['year']),)

    if ((__addon__.getSetting( "auto_download" ) == "true") and 
        (__addon__.getSetting( "auto_download_file" ) != os.path.basename( movieFullPath ))):
         self.item['autoDownload'] = True
         __addon__.setSetting("auto_download_file", "")

    for name in os.listdir(SERVICE_DIR):
#     FIX this to list from VFS of installed services    
      if os.path.isdir(os.path.join(SERVICE_DIR,name)): # and __addon__.getSetting( name ) == "true":
        service_list.append( name )
        service = name

    if len(self.item['tvshow']) > 0:
      def_service = __addon__.getSetting( "deftvservice")
    else:
      def_service = __addon__.getSetting( "defmovieservice")
      
    if service_list.count(def_service) > 0:
      service = def_service
    if len(service_list) > 0:  
      if len(service) < 1:
        self.item['service'] = service_list[0]
      else:
        self.item['service'] = service  

      
      self.item['service_list'] = service_list
      self.next = list(service_list)
      self.controlId = -1

      log( __name__ ,"Addon Version: [%s]"         % __version__)
      log( __name__ ,"Manual Search : [%s]"        % self.item['mansearch'])
      log( __name__ ,"Default Service : [%s]"      % self.item['service'])
      log( __name__ ,"Services : [%s]"             % self.item['service_list'])
      log( __name__ ,"Temp?: [%s]"                 % self.item['temp'])
      log( __name__ ,"Rar?: [%s]"                  % self.item['rar'])
      log( __name__ ,"File Path: [%s]"             % self.item['file_original_path'])
      log( __name__ ,"Year: [%s]"                  % str(self.item['year']))
      log( __name__ ,"Tv Show Title: [%s]"         % self.item['tvshow'])
      log( __name__ ,"Tv Show Season: [%s]"        % self.item['season'])
      log( __name__ ,"Tv Show Episode: [%s]"       % self.item['episode'])
      log( __name__ ,"Movie/Episode Title: [%s]"   % self.item['title'])
      log( __name__ ,"Subtitle Folder: [%s]"       % self.item['sub_folder'])
      log( __name__ ,"Languages: [%s]"             % self.item['full_language'])
      log( __name__ ,"Parent Folder Search: [%s]"  % self.item['parsearch'])
      log( __name__ ,"Stacked(CD1/CD2)?: [%s]"     % self.item['stack'])
  
    return self.item['autoDownload']

  def Search_Subtitles( self, gui = True ):
    self.item['subtitles_list'] = []
    if gui:
      self.getControl( SUBTITLES_LIST ).reset()
      self.getControl( LOADING_IMAGE ).setImage(
                                       xbmc.translatePath(
                                         os.path.join(
                                           SERVICE_DIR,
                                           self.item['service'],
                                           "logo.png")))

    exec ( "from services.%s import service as Service" % (self.item['service']))
    self.Service = Service
    if gui:
      self.getControl( STATUS_LABEL ).setLabel( _( 646 ) )

    socket.setdefaulttimeout(float(__addon__.getSetting( "timeout" )))
    try: 
      self.item = self.Service.search_subtitles(self.item)
    except socket.error:
      errno, errstr = sys.exc_info()[:2]
      if errno == socket.timeout:
        self.item['msg'] = _( 656 )
      else:
        self.item['msg'] =  "%s: %s" % ( _( 653 ),str(errstr[1]), )
    except:
      errno, errstr = sys.exc_info()[:2]
      self.item['msg'] = "Error: %s" % ( str(errstr), )
    socket.setdefaulttimeout(None)
    if gui:
      self.getControl( STATUS_LABEL ).setLabel( _( 642 ) % ( "...", ) )

    if not self.item['subtitles_list']:
      if __addon__.getSetting( "search_next" )== "true" and len(self.next) > 1:
        xbmc.sleep(1500)
        self.next.remove(self.item['service'])
        self.item['service'] = self.next[0]
        self.show_service_list(gui)
        log( __name__ ,"Auto Searching '%s' Service" % (self.item['service'],) )
        self.Search_Subtitles(gui)
      else:
        self.next = list(self.item['service_list'])
        if gui:
          select_index = 0
          if self.item['msg'] != "":
            self.getControl( STATUS_LABEL ).setLabel( self.item['msg'] )
          else:
            self.getControl( STATUS_LABEL ).setLabel( _( 657 ) )
          self.show_service_list(gui)
    else:
      subscounter = 0
      itemCount = 0
      list_subs = []
      for item in self.item['subtitles_list']:
        if (self.item['autoDownload'] and 
            item["sync"] and  
            (item["language_name"] == languageTranslate(
                languageTranslate(self.language_1,0,2),2,0)
            )):
          self.Download_Subtitles(itemCount, True, gui)
          __addon__.setSetting("auto_download_file",
                               os.path.basename( self.item['file_original_path'] ))
          return True
          break
        else:
          if gui:
            listitem = xbmcgui.ListItem(label=_( languageTranslate(item["language_name"],0,5) ),
                                        label2=item["filename"],
                                        iconImage=item["rating"],
                                        thumbnailImage=item["language_flag"]
                                       )
            if item["sync"]:
              listitem.setProperty( "sync", "true" )
            else:
              listitem.setProperty( "sync", "false" )

            if item.get("hearing_imp", False):
              listitem.setProperty( "hearing_imp", "true" )
            else:
              listitem.setProperty( "hearing_imp", "false" )
              
            self.item['list'].append(subscounter)
            subscounter = subscounter + 1
            list_subs.append(listitem)                                 
        itemCount += 1
      
      if gui:
        label = '%i %s '"' %s '"'' % (len ( self.item['subtitles_list'] ),_( 744 ),self.item['file_name'],)
        self.getControl( STATUS_LABEL ).setLabel( label ) 
        self.getControl( SUBTITLES_LIST ).addItems( list_subs )
        self.setFocusId( SUBTITLES_LIST )
        self.getControl( SUBTITLES_LIST ).selectItem( 0 )
      return False

  def Download_Subtitles( self, pos, auto = False, gui = True ):
    if gui:
      if auto:
        self.getControl( STATUS_LABEL ).setLabel(  _( 763 ) )
      else:
        self.getControl( STATUS_LABEL ).setLabel(  _( 649 ) )
    self.item['zip_subs'] = os.path.join( self.item['tmp_sub_dir'], "zipsubs.zip")
    self.item['pos'] = pos
    self.item = self.Service.download_subtitles(self.item)
    sub_lang = str(languageTranslate(self.item['language'],0,2))

    if self.item['zipped'] :
      self.Extract_Subtitles(self.item['zip_subs'],sub_lang, gui)
    else:
      sub_ext  = os.path.splitext( self.item['file'] )[1]
      sub_name = os.path.splitext( os.path.basename( self.item['file_original_path'] ) )[0]
      if (__addon__.getSetting( "lang_to_end" ) == "true"):
        file_name = u"%s.%s%s" % ( sub_name, sub_lang, sub_ext )
      else:
        file_name = u"%s%s" % ( sub_name, sub_ext )
      file_from = file.replace('\\','/')
      file_to = os.path.join(self.item['sub_folder'], file_name).replace('\\','/')
      # Create a files list of from-to tuples so that multiple files may be
      # copied (sub+idx etc')
      files_list = [(file_from,file_to)]
      # If the subtitle's extension sub, check if an idx file exists and if so
      # add it to the list
      if ((sub_ext == ".sub") and (os.path.exists(self.item['file'][:-3]+"idx"))):
          log( __name__ ,"found .sub+.idx pair %s + %s" % (file_from,file_from[:-3]+"idx"))
          files_list.append((file_from[:-3]+"idx",file_to[:-3]+"idx"))
      for cur_file_from, cur_file_to in files_list:
         subtitle_set,file_path  = copy_files( cur_file_from, cur_file_to )
      # Choose the last pair in the list, second item (destination file)
      if subtitle_set:
        subtitle = files_list[-1][1]
        xbmc.Player().setSubtitles(subtitle.encode("utf-8"))
        self.close()
      else:
        if gui:
          self.getControl( STATUS_LABEL ).setLabel( _( 654 ) )
          self.show_service_list(gui)

  def Extract_Subtitles( self, zip_subs, subtitle_lang, gui = True ):
    xbmc.executebuiltin(('XBMC.Extract("%s","%s")' % (zip_subs,self.item['tmp_sub_dir'],)).encode('utf-8'))
    xbmc.sleep(1000)
    files = os.listdir(self.item['tmp_sub_dir'])
    sub_filename = os.path.basename( self.item['file_original_path'] )
    exts = [".srt", ".sub", ".txt", ".smi", ".ssa", ".ass" ]
    subtitle_set = False
    if len(files) < 1 :
      if gui:
        self.getControl( STATUS_LABEL ).setLabel( _( 654 ) )
        self.show_service_list(gui)
    else :
      if gui:
        self.getControl( STATUS_LABEL ).setLabel( _( 652 ) )
      subtitle_set = False
      movie_sub = False
      episode = 0
      for zip_entry in files:
        if os.path.splitext( zip_entry )[1] in exts:
          subtitle_file, file_path = self.create_name(zip_entry,sub_filename,subtitle_lang)
          if len(self.item['tvshow']) > 0:
            title, season, episode = regex_tvshow(False, zip_entry)
            if not episode : episode = -1
          else:
            if os.path.splitext( zip_entry )[1] in exts:
              movie_sub = True
          if ( movie_sub or int(episode) == int(self.item['episode']) ):
            if self.item['stack']:
              try:
                for subName in self.item['stackPath']:
                  if (re.split("(?x)(?i)\CD(\d)",
                      zip_entry)[1]) == (re.split("(?x)(?i)\CD(\d)",
                      urllib.unquote ( subName ))[1]
                      ):
                    subtitle_file, file_path = self.create_name(
                                                    zip_entry,
                                                    urllib.unquote(os.path.basename(subName[8:])),
                                                    subtitle_lang
                                                               )
                    subtitle_set,file_path = copy_files( subtitle_file, file_path ) 
                if re.split("(?x)(?i)\CD(\d)", zip_entry)[1] == "1":
                  subToActivate = file_path
              except:
                subtitle_set = False              
            else:
              subtitle_set,subToActivate = copy_files( subtitle_file, file_path )

      if not subtitle_set:
        for zip_entry in files:
          if os.path.splitext( zip_entry )[1] in exts:
            subtitle_file, file_path = self.create_name(zip_entry,sub_filename,subtitle_lang)
            subtitle_set,subToActivate  = copy_files( subtitle_file, file_path )

    if subtitle_set :
      xbmc.Player().setSubtitles(subToActivate.encode("utf-8"))
      self.close()
    else:
      if gui:
        self.getControl( STATUS_LABEL ).setLabel( _( 654 ) )
        self.show_service_list(gui)
      
      
  def show_service_list(self,gui):
    try:
      select_index = self.item['service_list'].index(self.item['service'])
    except IndexError:
      select_index = 0
    if gui:
      self.setFocusId( SERVICES_LIST )
      self.getControl( SERVICES_LIST ).selectItem( select_index )

  def create_name(self,zip_entry,sub_filename,subtitle_lang): 
    if self.item['temp']:
      name = "temp_sub"
    else:
      name = os.path.splitext( sub_filename )[0]
    if (__addon__.getSetting( "lang_to_end" ) == "true"):
      file_name = u"%s.%s%s" % ( name, 
                                 subtitle_lang,
                                 os.path.splitext( zip_entry )[1] )
    else:
      file_name = u"%s%s" % ( name, os.path.splitext( zip_entry )[1] )
    log( __name__ ,"Sub in Zip [%s], File Name [%s]" % (zip_entry,
                                                        file_name,))
    ret_zip_entry = os.path.join(self.item['tmp_sub_dir'],zip_entry)
    ret_file_name = os.path.join(self.item['sub_folder'],file_name)
    return ret_zip_entry,ret_file_name

  def list_services( self ):
    self.item['list'] = []
    all_items = []
    self.getControl( SERVICES_LIST ).reset() 
    for serv in self.item['service_list']:
      listitem = xbmcgui.ListItem( serv )
      self.item['list'].append(serv)
      listitem.setProperty( "man", "false" )
      all_items.append(listitem)

    if self.item['mansearch'] :
        listitem = xbmcgui.ListItem( _( 612 ) )
        listitem.setProperty( "man", "true" )
        self.item['list'].append("Man")
        all_items.append(listitem)

    if self.item['parsearch'] :
        listitem = xbmcgui.ListItem( _( 747 ) )
        listitem.setProperty( "man", "true" )
        self.item['list'].append("Par")
        all_items.append(listitem)
      
    listitem = xbmcgui.ListItem( _( 762 ) )
    listitem.setProperty( "man", "true" )
    self.item['list'].append("Set")
    all_items.append(listitem)
    self.getControl( SERVICES_LIST ).addItems( all_items )    

  def keyboard(self, parent):
    dir, self.item['year'] = xbmc.getCleanMovieTitle(self.item['file_original_path'], self.item['parsearch'])
    if not parent:
      if self.item['man_search_str'] != "":
        srchstr = self.item['man_search_str']
      else:
        srchstr = "%s (%s)" % (dir,self.item['year'],)  
      kb = xbmc.Keyboard(srchstr, _( 751 ), False)
      text = self.item['file_name']
      kb.doModal()
      if (kb.isConfirmed()): text, self.item['year'] = xbmc.getCleanMovieTitle(kb.getText())
      self.item['title'] = text
      self.item['man_search_str'] = text
    else:
      self.item['title'] = dir   

    log( __name__ ,"Manual/Keyboard Entry: Title:[%s], Year: [%s]" % (self.item['title'], self.item['year'],))
    if self.item['year'] != "" :
      self.item['file_name'] = "%s (%s)" % (self.item['file_name'], str(self.item['year']),)
    else:
      self.item['file_name'] = self.item['title']   
    self.item['tvshow'] = ""
    self.next = list(self.item['service_list'])
    self.Search_Subtitles() 

  def onClick( self, controlId ):
    if controlId == SUBTITLES_LIST:
      self.Download_Subtitles( self.getControl( SUBTITLES_LIST ).getSelectedPosition() )
          
    elif controlId == SERVICES_LIST:
      xbmc.executebuiltin("Skin.Reset(SubtitleSourceChooserVisible)")
      selection = str(self.item['list'][self.getControl( SERVICES_LIST ).getSelectedPosition()]) 
      self.setFocusId( 120 )
   
      if selection == "Man":
        self.keyboard(False)
      elif selection == "Par":
        self.keyboard(True)
      elif selection == "Set":
        __addon__.openSettings()
        self.set_allparam()
        self.on_run()        
      else:
        self.item['service'] = selection
        self.next = list(self.item['service_list'])
        self.Search_Subtitles()      

  def onFocus( self, controlId ):
    if controlId == 150:
      try:
        select_index = self.item['service_list'].index(self.item['service'])
      except IndexError:
        select_index = 0
      self.getControl( SERVICES_LIST ).selectItem(select_index)
    self.controlId = controlId
    try:
      if controlId == 8999:
        self.setFocusId( 150 )
    except:
      pass

  def onAction( self, action ):
    if ( action.getId() in CANCEL_DIALOG):
      self.close()

