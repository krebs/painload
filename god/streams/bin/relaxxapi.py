#!/usr/bin/python2
import json
from urllib import quote
class relaxx:

    def __init__(self,relaxxurl="http://lounge.mpd.shack/"):
        self.baseurl=relaxxurl
        import requests
        ret = requests.get(relaxxurl) # grab cookie
        try:
            self.r = requests.session(cookies=ret.cookies,headers={"Referer":relaxxurl})
        except:
            print ("you are missing the `requests` dependency, please do a `pip install requests`")
    def _status(self,value=0,data="json=null"):
        """
        value is some weird current playlist value, 0 seems to work
        data is url encoded kv-store
        """
        # TODO get the current playlist value
        url=self.baseurl+"include/controller-ping.php?value=%s"%value
        return self.r.post(url,data="json=null").text

    def _playlist(self,action,value="",json="null",method="get"):
        """
        This function is the interface to the controller-playlist api
            use it if you dare
        Possible actions:
            clear
            addSong url_encoded_path
            moveSong 1:2
            getPlaylists
            getPlaylistInfo 1
            listPlaylistInfo
        as everything seems to be a get request, the method is set to GET as
        default
        """
        url=self.baseurl+"include/controller-playlist.php?action=%s&value=%s&json=%s"%(action,value,json)
        if method== "get":
            return self.r.get(url).text
        elif method == "post":
            return r.post(url).text
        else:
            raise Exception("unknown method %s")

    def _playback(self,action,value="",json="null",method="get"):
        """
        play
        continue
        stop
        setCrossfade
        """
        url=self.baseurl+"include/controller-playback.php?action=%s&value=%s&json=%s"%(action,value,json)
        # probably obsolete because everything is "get"
        if method== "get":
            return self.r.get(url).text
        elif method == "post":
            return r.post(url).text
        else:
            raise Exception("unknown method %s")

    def _radio(self,playlist=""):
        """
        both, post and get the url seem to work here...
        """
        url=self.baseurl+"include/controller-netradio.php?playlist=%s"%quote(playlist)
        return self.r.get(url).text

    def add_radio(self,playlist=""):
        print playlist
        print self._radio(playlist)
        print json.loads(self._radio(playlist)) #[1:-1])["url"]
        resolved_url= json.loads(self._radio(playlist)[1:-1])["url"]
        self.add_song(resolved_url)

    def add_song(self,path):
        return self._playlist("addSong",path)

    def get_first(self):
        return json.loads(self._playlist("getPlaylistInfo","0",""))[0]

    def get_last(self):
        return json.loads(self._playlist("getPlaylistInfo","0",""))[-1]

    def clear(self):
        return self._playlist("clear")
    
    def crossfade(self,ident="0"):
        """
        default: no crossfade
        """
        return self._playback("setCrossfade",ident)

    def repeat(self,ident="1"):
        """
        default: do repeat
        """
        return self._playback("repeat",ident)

    def play(self,ident):
        return self._playback("play",ident)

    def stop(self):
        return self._playback("stop")

    def cont(self,ident):
        return self._playback("continue",ident)

    def play_first(self):
        return self.play(self.get_first()["Id"])

    def play_last(self):
        return self.play(self.get_last()["Id"])

    def state(self):
        return json.loads(self._status())

    def is_running(self):
        return self.state()["status"]["state"] == "play"

    def playing(self):
        """ returns "" if not running
        """
        state = self.state()
        if state["status"]["state"] == "play" :
            ident = state["status"]["song"]
            current = state["playlist"]["file"][int(ident)]
            return current.get("Name",current.get("Artist","unkown artist")) + " - " + current.get("Title","unknown title")
        else:
            return ""

if __name__ == "__main__":
    r = relaxx()
    print r.state()
    print r.playing()
    print r.add_radio("http://deluxetelevision.com/livestreams/radio/DELUXE_RADIO.pls")
    #print r.clear()
    #print r.add_radio("http://somafm.com/lush.pls")
    #print r.get_first()["Id"]
    #print r.play_first()
    #print r.add_radio("http://somafm.com/lush.pls")
