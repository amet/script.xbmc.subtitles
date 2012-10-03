# -*- coding: utf-8 -*-

import os
import re
import sys
import xbmc, xbmcaddon
import urllib
import socket
import xbmcgui, xbmcvfs

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
    self.runGUI()

  def runGUI( self ):
    if not xbmc.getCondVisibility("VideoPlayer.HasSubtitles"):
      self.getControl( 111 ).setVisible( False )
    self.list_services()
    self.Search_Subtitles()

  def set_allparam(self):
    self.item                   = dict()
    self.item['list']           = []
    self.item['services']       = []
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
    self.item['lang_to_end']    =__addon__.getSetting( "lang_to_end" ) == "true"
    
    
    service_list        = []
    service             = ""
    use_subs_folder     = __addon__.getSetting( "use_subs_folder" ) == "true"                                  # use 'Subs' subfolder for storing subtitles
    movieFullPath       = urllib.unquote(xbmc.Player().getPlayingFile().decode('utf-8'))                       # Full path of a playing file
    movieFolderForSubs  = __addon__.getSetting( "subfolder" ) == "true"                                        # True for movie folder
    
    clean_temp(self.item)                                                                                      # clean temp dirs
    set_languages(self.item)                                                                                   # Get all languages

    if ( movieFullPath.find("http") > -1 ):
      self.item['sub_folder'] = self.item['stream_sub_dir']
      self.item['temp'] = True

    elif ( movieFullPath.find("rar://") > -1 ):
      self.item['rar'] = True
      movieFullPath = os.path.dirname(movieFullPath[6:])
  
    
    elif ( movieFullPath.find("stack://") > -1 ):
      self.item['stackPath'] = xbmcvfs.listdirWithDetails(movieFullPath)[1]
      movieFullPath = self.item['stackPath'][0]
      self.item['stack'] = True

    if movieFolderForSubs:
      if use_subs_folder:
        self.item['sub_folder'] = os.path.join(os.path.dirname( movieFullPath ),'Subs')
        xbmcvfs.mkdirs(self.item['sub_folder'])
      else:
        self.item['sub_folder'] = os.path.dirname( movieFullPath )
    
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
    self.item['file_name'] = os.path.basename( movieFullPath )                     # Display Movie name or search string

    if ((__addon__.getSetting( "auto_download" ) == "true") and 
        (__addon__.getSetting( "auto_download_file" ) != os.path.basename( movieFullPath ))):
         self.item['autoDownload'] = True
         __addon__.setSetting("auto_download_file", "")
         xbmc.executebuiltin((u"Notification(%s,%s,-1)" % (__scriptname__, _(763))).encode("utf-8"))
         

    service_id_list = xbmcvfs.listdir("addons://enabled/xbmc.subtitle.module/")[1]
    if not service_id_list:
      xbmc.executebuiltin('XBMC.ActivateWindow(addonbrowser, addons://all/xbmc.subtitle.module)') # this is something we need to workout once 
                                                                                                  # repo is setup to use this extension point
      return True # to close the script
    for id in service_id_list:
      name = xbmcaddon.Addon(id).getAddonInfo('name')
      logo = xbmcaddon.Addon(id).getAddonInfo('icon')
      self.item['services'].append({"name":name, "logo": logo})
      service_list.append( name )
      service = name


    if len(self.item['tvshow']) > 0:
      def_service = __addon__.getSetting( "deftvservice")
    else:
      def_service = __addon__.getSetting( "defmovieservice")
      
    if service_id_list.count(def_service) > 0:
      service = xbmcaddon.Addon(def_service).getAddonInfo('name')
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
      log( __name__ ,"Auto Download: [%s]"         % self.item['autoDownload'])
  
    return self.item['autoDownload']

  def Search_Subtitles( self, gui = True ):
    if not self.item['services']:
      return True # no services found, return True to close the script
    self.item['subtitles_list'] = []
    if gui:
      self.getControl( STATUS_LABEL ).setLabel( _( 646 ) )
      self.getControl( SUBTITLES_LIST ).reset()
      for s in self.item['services']:
        if s["name"] == self.item['service']:
          self.getControl( LOADING_IMAGE ).setImage(s["logo"])
          break
      
    exec ( "from %s import service as Service" % (self.item['service']))
    self.Service = Service

    socket.setdefaulttimeout(float(__addon__.getSetting( "timeout" )))
    try: 
      self.item = self.Service.Search(self.item)
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
      
    __addon__.setSetting("auto_download_file",os.path.basename( self.item['file_original_path'] ))
    
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
      if self.item['autoDownload']:
        xbmc.executebuiltin((u"Notification(%s,%s,%i)" % (__scriptname__, _(767), 1000)).encode("utf-8"))  
    else:
      subscounter = 0
      itemCount = 0
      list_subs = []
      for item in self.item['subtitles_list']:
        # this will check what was returned from service, 
        # full language, 2 letter code or 3 letter code and always thanslate it to full language if needed
        item["language"] = get_language(item["language"])
        
        if (self.item['autoDownload'] and 
            item.get("sync", True) and  
            (item["language"] == languageTranslate(__addon__.getSetting( "Lang01" ), 3, 0)
            )):
          self.Download_Subtitles(itemCount, True, gui)
          if self.item['autoDownload']:
            xbmc.executebuiltin((u"Notification(%s,%s,%i)" % (__scriptname__, _(765), 1000)).encode("utf-8"))
          return True
        else:
          if gui:
            listitem = xbmcgui.ListItem(label=_( languageTranslate(item["language"],0,4) ),
                                        label2=item["filename"],
                                        iconImage=item["rating"],
                                        thumbnailImage="flags/%s.gif" % languageTranslate(item["language"],0,1)
                                       )
            if item.get("sync", True):
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
    
    self.item['pos'] = pos
    
    if gui:
      if auto:
        self.getControl( STATUS_LABEL ).setLabel(  _( 763 ) )
      else:
        self.getControl( STATUS_LABEL ).setLabel(  _( 649 ) )

    downloadedSubtitleList = self.Service.Download(self.item)
    subtitlesToActivate = []
    if downloadedSubtitleList != None:     
      if self.item['stack']:
        for i in range(len(downloadedSubtitleList)):
          result = self.copyFiles(downloadedSubtitleList[i],self.item['stackPath'][i])
          subtitlesToActivate.append(result)
      else:
        result = self.copyFiles(downloadedSubtitleList[0],self.item['file_original_path'])
        subtitlesToActivate = [result,]
        
      if xbmcvfs.exists(subtitlesToActivate[0]):
        log( __name__ ,"Activating [%s] Subtitle" % subtitlesToActivate[0])
        xbmc.Player().setSubtitles(subtitlesToActivate[0].encode("utf-8"))
        self.close()
    if gui:
      self.getControl( STATUS_LABEL ).setLabel( _( 654 ) )
      self.show_service_list(gui)
      
  def copyFiles(self,downloadedSubtitle, playingFile):
    if (self.item['lang_to_end']):
      sub_lang = str(languageTranslate(self.item['subtitles_list'][self.item['pos']][ "language" ],0,1))
    else:
      sub_lang = ""  
    sub_ext  = os.path.splitext( downloadedSubtitle )[1]
    sub_name = os.path.splitext( os.path.basename( playingFile ) )[0]
  
    file_name = u"%s.%s%s" % ( sub_name, sub_lang, sub_ext )
  
    # Create a files list of from-to tuples so that multiple files may be
    # copied (sub+idx etc')
    files_list = [(downloadedSubtitle,xbmc.validatePath(os.path.join(self.item['sub_folder'], file_name)))]
    
    # If the subtitle's extension sub, check if an idx file exists and if so
    # add it to the list
    if ((sub_ext == ".sub") and (xbmcvfs.exists(downloadedSubtitle[:-3]+"idx"))):
      log( __name__ ,"found .sub+.idx pair %s + %s" % (file_from,file_from[:-3]+"idx"))
      files_list.append((file_from[:-3]+"idx",file_to[:-3]+"idx"))
    for cur_file_from, cur_file_to in files_list:
      xbmcvfs.copy( cur_file_from, cur_file_to )
    return files_list[0][1]
      
  def show_service_list(self,gui):
    try:
      select_index = self.item['service_list'].index(self.item['service'])
    except IndexError:
      select_index = 0
    if gui:
      self.setFocusId( SERVICES_LIST )
      self.getControl( SERVICES_LIST ).selectItem( select_index )

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
      if (kb.isConfirmed()):
        text, self.item['year'] = xbmc.getCleanMovieTitle(kb.getText())
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
        self.runGUI()        
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

