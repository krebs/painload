# jsb/plugs/common/weather.py
#
#

""" show weather based on Google's weather API """

__copyright__ = 'this file is in the public domain'
__author__ = 'Landon Fowles'

## jsb imports

from jsb.utils.url import geturl
from jsb.utils.generic import getwho
from jsb.lib.commands import cmnds
from jsb.lib.persist import Persist
from jsb.lib.examples import examples
from jsb.lib.persiststate import UserState

## basic imports

from xml.dom import minidom
from urllib import urlencode
import logging
import time

## weather command

def handle_weather(bot, ievent):
    """ show weather using Google's weather API """
    userhost = ""
    loc = ""
    try:
        nick = ievent.rest
        if nick:
            userhost = getwho(bot, nick)
            if not userhost: pass
            else:
                try:
                    name = bot.users.getname(userhost)
                    if not name: ievent.reply("%s is not known with the bot" % nick) ; return
                    us = UserState(name)
                    loc = us['location']
                except KeyError: ievent.reply("%s doesn't have his location set in userstate" % nick) ; return
    except KeyError: pass
    if not loc:
        if ievent.rest: loc = ievent.rest
        else: ievent.missing('<nick>|<location>') ; return
    query = urlencode({'weather':loc})
    weathertxt = geturl('http://www.google.ca/ig/api?%s' % query)
    if 'problem_cause' in weathertxt:
        logging.error('weather - %s' % weathertxt)
        ievent.reply('an error occured looking up data for %s' % loc)
        return
    logging.debug("weather - got reply: %s" % weathertxt)
    resultstr = ""
    if weathertxt:
        gweather = minidom.parseString(weathertxt)
        gweather = gweather.getElementsByTagName('weather')[0]
        if ievent.usercmnd == "weather":
            info = gweather.getElementsByTagName('forecast_information')[0]
            if info:
                city = info.getElementsByTagName('city')[0].attributes["data"].value
                zip = info.getElementsByTagName('postal_code')[0].attributes["data"].value
                time = info.getElementsByTagName('current_date_time')[0].attributes["data"].value
                weather = gweather.getElementsByTagName('current_conditions')[0]
                condition = weather.getElementsByTagName('condition')[0].attributes["data"].value
                temp_f = weather.getElementsByTagName('temp_f')[0].attributes["data"].value
                temp_c = weather.getElementsByTagName('temp_c')[0].attributes["data"].value
                humidity = weather.getElementsByTagName('humidity')[0].attributes["data"].value
                try: wind = weather.getElementsByTagName('wind_condition')[0].attributes["data"].value
                except IndexError: wind = ""
                try: wind_km = round(int(wind[-6:-4]) * 1.609344)
                except ValueError: wind_km = ""
                if (not condition == ""): condition = " Oh, and it's " + condition + "."
                resultstr = "As of %s, %s (%s) has a temperature of %sC/%sF with %s. %s (%s km/h).%s" % (time, city, zip, temp_c, temp_f, humidity, wind, wind_km, condition)
        elif ievent.usercmnd == "forecast":
            forecasts = gweather.getElementsByTagName('forecast_conditions')
            for forecast in forecasts:
                condition = forecast.getElementsByTagName('condition')[0].attributes["data"].value
                low_f = forecast.getElementsByTagName('low')[0].attributes["data"].value
                high_f = forecast.getElementsByTagName('high')[0].attributes["data"].value
                day = forecast.getElementsByTagName('day_of_week')[0].attributes["data"].value
                low_c = round((int(low_f) - 32) * 5.0 / 9.0)
                high_c = round((int(high_f) - 32) * 5.0 / 9.0)
                resultstr += "[%s: F(%sl/%sh) C(%sl/%sh) %s]" % (day, low_f, high_f, low_c, high_c, condition)
    if not resultstr: ievent.reply('%s not found!' % loc) ; return
    else: ievent.reply(resultstr)

cmnds.add('weather', handle_weather, ['OPER', 'USER', 'GUEST'])
examples.add('weather', 'get weather for <LOCATION> or <nick>', '1) weather London, England 2) weather dunker')
