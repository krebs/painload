# lib/utils/timeutils.py
#
#

""" time related helper functions. """

## jsb imports

from exception import handle_exception

## basic imports

import time
import re
import calendar

## defines

leapfactor = float(6*60*60)/float(365*24*60*60)
timere = re.compile('(\S+)\s+(\S+)\s+(\d+)\s+(\d+):(\d+):(\d+)\s+(\d+)')
bdmonths = ['Bo', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

## elapsedstring function 

def elapsedstring(nsec, ywd = None):
    """ given the number of seconds return a string of the elapsed time. """
    nsec = int(float(nsec))
    year = 365*24*60*60
    week = 7*24*60*60
    day = 24*60*60
    hour = 60*60
    minute = 60
    nsec -= nsec * leapfactor
    years = int(nsec/year)
    nsec -= years*year
    weeks = int(nsec/week)
    nsec -= weeks*week
    days = int(nsec/day)
    nsec -= days*day
    hours = int(nsec/hour)
    nsec -= hours*hour
    minutes = int(nsec/minute)
    sec = int(nsec - minutes*minute)   
    result = ''
    if (years > 1): result = str(years) + " years "
    if (years == 1): result = "1 year "
    if (weeks > 1): result += str(weeks) + " weeks "
    if (weeks == 1): result += "1 week "
    if (days > 1):
        if ywd: result += 'and '+ str(days) + " days"
        else: result += str(days) + " days "
    if (days == 1):
        if ywd: result += 'and 1 day'
        else: result += "1 day "
    if ywd: return result
    if (hours > 1): result += str(hours) + " hours "
    if (hours == 1): result += "1 hour "
    if (minutes > 1): result += str(minutes) + " minutes "
    if (minutes == 1): result += "1 minute "
    if sec == 0:
        if result: return result
        else: return 0
    if (sec == 1):
        if result: result += "and 1 second "
        else: result = "1 second"
    else:
        if result: result += "and " + str(sec) + " seconds"
        else:  result = str(sec) + " seconds"
    return result.strip()

## hourmin function

def hourmin(ttime):
    """ return the hours:minutes of a unix timestamp. """
    result = ""
    timeres = time.localtime(ttime)
    if timeres[3] < 10: result += "0" + str(timeres[3]) + ":"
    else: result += str(timeres[3]) + ":"
    if timeres[4] < 10: result += "0" + str(timeres[4])
    else: result += str(timeres[4])
    return result

## striptime function

def striptime(what):
    """ strip time indicators from string. """
    what = str(what)
    what = re.sub('\d+-\d+-\d+', '', what)
    what = re.sub('\d+-\d+', '', what)
    what = re.sub('\d+:\d+', '', what)
    what = re.sub('\s+', ' ', what)
    return what.strip()

## now function

def now():
    """ return current time. """
    if time.daylight: ttime = time.ctime(time.time() + int(time.timezone) + 3600)
    else: ttime = time.ctime(time.time() + int(time.timezone))
    return ttime

## today function

def today():
    """ return time of 0:00 today. """
    if time.daylight: ttime = time.ctime(time.time() + int(time.timezone) + 3600)
    else: ttime = time.ctime(time.time() + int(time.timezone))
    matched = re.search(timere, ttime)
    if matched:
        temp = "%s %s %s" % (matched.group(3), matched.group(2), matched.group(7))
        timestring = time.strptime(temp, "%d %b %Y")
        result = time.mktime(timestring)
        return result

## strtotime function

def strtotime(what):
    """ convert string to time. """
    daymonthyear = 0
    hoursmin = 0
    try:
        dmyre = re.search('(\d+)-(\d+)-(\d+)', str(what))
        if dmyre:
            (day, month, year) = dmyre.groups()
            day = int(day)
            month = int(month)
            year = int(year)
            if day <= calendar.monthrange(year, month)[1]:
                date = "%s %s %s" % (day, bdmonths[month], year)
                daymonthyear = time.mktime(time.strptime(date, "%d %b %Y"))
            else: return None
        else:
            dmre = re.search('(\d+)-(\d+)', str(what))
            if dmre:
                year = time.localtime()[0]
                (day, month) = dmre.groups()
                day = int(day)
                month = int(month)
                if day <= calendar.monthrange(year, month)[1]: 
                    date = "%s %s %s" % (day, bdmonths[month], year)
                    daymonthyear = time.mktime(time.strptime(date, "%d %b %Y"))
                else: return None
        hmsre = re.search('(\d+):(\d+):(\d+)', str(what))
        if hmsre:
            (h, m, s) = hmsre.groups()
            h = int(h)
            m = int(m)
            s = int(s)
            if h > 24 or h < 0 or m > 60 or m < 0 or s > 60 or s < 0: return None
            hours = 60 * 60 * (int(hmsre.group(1)))
            hoursmin = hours  + int(hmsre.group(2)) * 60
            hms = hoursmin + int(hmsre.group(3))
        else:
            hmre = re.search('(\d+):(\d+)', str(what))
            if hmre:
                (h, m) = hmre.groups()
                h = int(h)
                m = int(m)
                if h > 24 or h < 0 or m > 60 or m < 0: return None
                hours = 60 * 60 * (int(hmre.group(1)))
                hms = hours  + int(hmre.group(2)) * 60
            else: hms = 0
        if not daymonthyear and not hms: return None
        if daymonthyear == 0: heute = today()
        else: heute = daymonthyear
        return heute + hms
    except OverflowError: return None
    except ValueError:return None
    except Exception, ex: pass

def strtotime2(what):
    """ convert string to time. """
    daymonthyear = 0
    hoursmin = 0
    try:
        dmyre = re.search('(\d+)-(\d+)-(\d+)', str(what))
        if dmyre:
            (year, month, day) = dmyre.groups()
            day = int(day)
            month = int(month)
            year = int(year)
            if day <= calendar.monthrange(year, month)[1]:
                date = "%s %s %s" % (day, bdmonths[month], year)
                daymonthyear = time.mktime(time.strptime(date, "%d %b %Y"))
            else: return None
        else:
            dmre = re.search('(\d+)-(\d+)', str(what))
            if dmre:
                year = time.localtime()[0]
                (day, month) = dmre.groups()
                day = int(day)
                month = int(month)
                if day <= calendar.monthrange(year, month)[1]: 
                    date = "%s %s %s" % (day, bdmonths[month], year)
                    daymonthyear = time.mktime(time.strptime(date, "%d %b %Y"))
                else: return None
        hmsre = re.search('(\d+):(\d+):(\d+)', str(what))
        if hmsre:
            (h, m, s) = hmsre.groups()
            h = int(h)
            m = int(m)
            s = int(s)
            if h > 24 or h < 0 or m > 60 or m < 0 or s > 60 or s < 0: return None
            hours = 60 * 60 * (int(hmsre.group(1)))
            hoursmin = hours  + int(hmsre.group(2)) * 60
            hms = hoursmin + int(hmsre.group(3))
        else:
            hmre = re.search('(\d+):(\d+)', str(what))
            if hmre:
                (h, m) = hmre.groups()
                h = int(h)
                m = int(m)
                if h > 24 or h < 0 or m > 60 or m < 0: return None
                hours = 60 * 60 * (int(hmre.group(1)))
                hms = hours  + int(hmre.group(2)) * 60
            else: hms = 0
        if not daymonthyear and not hms: return None
        if daymonthyear == 0: heute = today()
        else: heute = daymonthyear
        return heute + hms
    except OverflowError: return None
    except ValueError:return None
    except Exception, ex: pass

## uurminsec function

def uurminsec(ttime):
    """ return hours:minutes:seconds of the given time. """
    result = ""
    timeres = time.localtime(ttime)
    if timeres[3] < 10: result += "0" + str(timeres[3]) + ":"
    else: result += str(timeres[3]) + ":"
    if timeres[4] < 10: result += "0" + str(timeres[4]) + ":"
    else: result += str(timeres[4]) + ":"
    if timeres[5] < 10: result += "0" + str(timeres[5])
    else: result += str(timeres[5])
    return result

## getdaymonth function

def getdaymonth(ttime):
    """ return day-month of the given time. """
    timestr = time.ctime(ttime)
    result = re.search(timere, timestr)
    if result: return (result.group(3), result.group(2))
    else: return (None, None)

## getdaymonthyear function

def getdaymonthyear(ttime):
    """ return day-month-year of the given time. """
    timestr = time.ctime(ttime)
    result = re.search(timere, timestr)
    if result: return (result.group(3), result.group(2), result.group[7])
    else: return (None, None, None)

## dmy function

def dmy(ttime):
    """ return day month year as a string. """
    timestr = time.ctime(ttime)
    result = re.search(timere, timestr)
    if result: return "%s %s %s" % (result.group(3), result.group(2), result.group(7))
