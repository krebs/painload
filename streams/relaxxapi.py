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

    def _action(self,action,value="",json="null",method="get"):
        """
        This function is the interface to the controller-playlist api
            use it if you dare
        Possible actions:
            clear
            play
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
    def add_radio(self,playlist=""):
        """
        both, post and get the url seem to work here...
        """
        url=self.baseurl+"include/controller-netradio.php?playlist=%s"%playlist
        print self.r.post(url).text
        resolved_url= json.loads(self.r.get(url).text[1:-1])["url"]
        self.add_song(resolved_url)

    def add_song(self,path):
        return self._action("addSong",quote(path))

    def clear(self):
        return self._action("clear")

    def play(self,ident):
        return self._action("play",ident)

    def stop(self):
        return self._action("stop")
    def get_first(self):
        return json.loads(self._action("getPlaylistInfo","0",""))[0]

    def play_first(self):
        return self.play(self.get_first()["Id"])

    def state(self):
        return self._action(

if __name__ == "__main__":
    r = relaxx()
    r.stop()
    print r.play_first()
    #print r.add_radio("http://somafm.com/lush.pls")
