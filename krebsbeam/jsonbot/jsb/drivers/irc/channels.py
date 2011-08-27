# gozerbot/channels.py
#
#

""" 
    channel related data. implemented with a persisted dict of dicts. 
    
    :example:

        key = channels[event.channel]['key']

"""

## jsb imports

from jsb.utils.pdod import Pdod

class Channels(Pdod):

    """ 
        channels class .. per channel data. 

        :param fname: filename to persist the data to
        :type fname: string

    """

    def __init__(self, fname):

        # call base constructor
        Pdod.__init__(self, fname)

        # make sure attributes are initialised
        for j in self.data.values():
            if not j.has_key('perms'):
                j['perms'] = []
            if not j.has_key('autovoice'):
                j['autovoice'] = 0

    def __setitem__(self, a, b):

        # if item is not in dict initialise it to empty dict
        if not self.data.has_key(a):
           self.data[a] = {}

        # assign data
        self.data[a] = b 

    def getchannels(self):

        """
            return channels.

        """

        result = [] # list of channels found

        # loop over channels
        for channel in self.data.keys():
            channel = channel.strip()
            if channel not in result:
                result.append(channel)

        return result

    def getchannelswithkeys(self):

        """
            return channels with keys.

        """

        result = []

        # loop over channels gathering channel name and key
        for channel in self.data.keys():
            channel = channel.strip()
            try:
                key = self.data[channel]['key']
                if not channel + ' ' + key in result:
                    result.append(channel + ' ' + key)
            except KeyError:
                if channel not in result:
                    result.append(channel)

        return result

    def getkey(self, channel):

        """ 
            return key of channel if set.

            :param channel: channel to get key from
            :type channel: string

        """

        try:
            key = self.data[channel]['key']
        except:
            key = None

        return key

    def getnick(self, channel):

        """ 
            return bot nick of channel if set.

            :param channel: channel to get key from
            :type channel: string

        """

        try:
            nick = self.data[channel]['nick']
        except:
            nick = None

        return nick
