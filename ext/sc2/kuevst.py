from urllib.request import urlopen
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import pytz


def get_name(data):
    """ Returns the name of the event """
    n = data.a.string
    return n


def get_cd(data):
    """ Returns the countdown of the event
    e.g. event sign up ends on 10:00 on November 4th
    currently is 03:00, November 3rd
    returns: datetime object with the following info
    +1day7hours
    """
    cdTime = datetime.strptime(
        data.text[1:-5] + ' +0900', '%B %d, %Y - %H:%M %z')
    currentTime = datetime.now(tz=pytz.timezone('Asia/Seoul'))
    return cdTime - currentTime


def get_time(data):
    """ Returns the start date of the event """
    eventTime = datetime.strptime(data.text[1:-5], '%B %d, %Y - %H:%M')
    allTimes = time_to_times(eventTime)
    eventTimeStr = times_to_string(allTimes)
    return eventTimeStr


def time_to_times(data):
    """ Returns the event date for 3 timeszones """
    timeKR = pytz.timezone('Asia/Seoul').localize(data)
    timeAM = timeKR.astimezone(pytz.timezone('PST8PDT'))
    timeEU = timeKR.astimezone(pytz.timezone('Europe/Berlin'))
    return timeKR, timeEU, timeAM


def times_to_string(data):
    """ Returns beautiful date data """
    mmKR, ddKR, hhKR, ampmKR, tzKR = data[0].strftime("%B"), data[0].strftime("%#d").lstrip('0'), data[0].strftime("%#I").lstrip('0'), data[0].strftime("%p").lower(), data[0].strftime("%Z")
    timeStr = '{} {}, {}{} {} '.format(mmKR, ddKR, hhKR, ampmKR, tzKR)
    if data[1].strftime("%d") == data[0].strftime("%d"):
        hhEU, ampmEU, tzEU = data[1].strftime("%#I").lstrip('0'), data[1].strftime("%p").lower(), data[1].strftime("%Z")
        timeStr += '( {}{} {} '.format(hhEU, ampmEU, tzEU)
    else:
        mmEU, ddEU, hhEU, ampmEU, tzEU = data[1].strftime("%b"), data[1].strftime("%#d").lstrip('0'), data[1].strftime("%#I").lstrip('0'), data[1].strftime("%p").lower(), data[1].strftime("%Z")
        timeStr += '( {} {}, {}{} {} '.format(mmEU, ddEU, hhEU, ampmEU, tzEU)
    if data[2].strftime("%d") == data[0].strftime("%d"):
        hhAM, ampmAM, tzAM = data[2].strftime("%#I").lstrip('0').lstrip('0'), data[2].strftime("%p").lower(), data[2].strftime("%Z")
        timeStr += '/ {}{} {} )'.format(hhAM, ampmAM, tzAM)
    else:
        mmAM, ddAM, hhAM, ampmAM, tzAM = data[2].strftime("%b"), data[2].strftime("%#d").lstrip('0'), data[2].strftime("%#I").lstrip('0'), data[2].strftime("%p").lower(), data[2].strftime("%Z")
        timeStr += '/ {} {}, {}{} {} )'.format(mmAM, ddAM, hhAM, ampmAM, tzAM)
    return timeStr


def get_mode(data):
    """ Nothing to see here, literally """
    return None


def get_rsl(data, sL):
    """ Returns Region, Server and/or League information """
    r = data('td')[5].text.split('(')[0][1:-1]
    if len(data('td')[5].text.split('(')) == 2:
        s = data('td')[5].text.split('(')[1][0:-2]
    else:
        s = None
    if len(data('td')[4].text.split('(')) == 2:
        l = data('td')[4].text.split('(')[0][1:]
    else:
        l = data('td')[4].text.split('(')[0][1:-1]
    if l == 'Online Qualifier':
        l = None
    if l == 'Online':
        l = None
    if l == 'Offline':
        l = None
    return r, s, l


def get_prize(data):
    """ Returns any prizepool, if any """
    if data.string == None:
        for el in range(0, len(data.text.split('+'))):
            if el == 0:
                pr = data.text.split('+')[el][1:]
            elif el == len(data.text.split('+')) - 1:
                pr += ' + ' + data.text.split('+')[el][1:-1]
            else:
                pr += ' + ' + data.text.split('+')[el][1:]
        if pr[-1:] == '\n':
            pr = pr[:-1]
    else:
        pr = data.string[1:-1]
    if pr == "":
        pr = None
    elif pr == "-":
        pr = None
    return pr


def get_bracket(data):
    """ Returns the bracket, which is in nearly all cases the signup page as well """
    if data.find(class_="lp-icon lp-challonge") != None:
        b = data.find(class_="lp-icon lp-challonge").parent.get('href')
    elif data.find(class_="lp-icon lp-bracket") != None:
        b = data.find(class_="lp-icon lp-bracket").parent.get('href')
    else:
        b = None
    return b


def get_matcherino(data):
    """ Returns Matcherino information """
    if data.find(class_="lp-icon lp-matcherino") != None:
        ma = data.find(class_="lp-icon lp-matcherino").parent.get('href')
    else:
        ma = None
    return ma

def get_matcherino_code(data):
    if data.find(class_="lp-icon lp-matcherino") != None:
        code = data.find(class_="lp-icon lp-matcherino").parent.parent.get('title')
    else:
        code = None
    return code


def steal(tourType=None):
    if tourType == 'general':
        link = 'http://liquipedia.net/starcraft2/User:(16thSq)_Kuro/Open_Tournaments'
    elif tourType == 'amateur':
        link = 'http://liquipedia.net/starcraft2/User:(16thSq)_Kuro/Amateur_Tournaments'
    elif tourType == 'team':
        link = 'http://liquipedia.net/starcraft2/User:(16thSq)_Kuro/Team_Tournaments'
    page = urlopen(link)
    soup = BeautifulSoup(page, 'html.parser')
    if tourType == 'general':
        tableTour = soup.find_all('table')[1]
    elif tourType == 'amateur':
        tableTour = soup.find_all('table')[0]
    elif tourType == 'team':
        tableTour = soup.find_all('table')[1]
    events = [['1'] * 8 for x in range(len(tableTour('tr')) - 2)]
    for tRow in range(2, len(tableTour('tr'))):
        countdown = get_cd(tableTour('tr')[tRow]('td')[0])
        date = get_time(tableTour('tr')[tRow]('td')[1])
        mode = get_mode(tableTour('tr')[tRow]('td')[2])
        name = get_name(tableTour('tr')[tRow]('td')[3])
        region, server, league = get_rsl(tableTour('tr')[tRow], tourType)
        prize = get_prize(tableTour('tr')[tRow]('td')[6])
        matcherino = get_matcherino(tableTour('tr')[tRow]('td')[7])
        matcherinoCode = get_matcherino_code(tableTour('tr')[tRow]('td')[7])
        bracket = get_bracket(tableTour('tr')[tRow]('td')[7])
        events[tRow - 2] = [name, date, region, league, server, prize,
                            matcherino, matcherinoCode, bracket, countdown, mode]
    return events
