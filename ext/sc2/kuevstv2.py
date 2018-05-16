from datetime import datetime
import pytz


def get_cd(data):
    """ Returns the countdown of the event
    e.g. event sign up ends on 10:00 on November 4th
    currently is 03:00, November 3rd
    returns: datetime object with the following info
    +1day7hours
    """
    cdTime = datetime.strptime(data + ' +0900', '%B %d, %Y - %H:%M {{Abbr/KST}} %z')
    currentTime = datetime.now(tz=pytz.timezone('Asia/Seoul'))
    return cdTime - currentTime


def get_time(data):
    """ Returns the start date of the event """
    eventTime = datetime.strptime(data, '%B %d, %Y - %H:%M {{Abbr/KST}}')
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
    timeStr = f'{mmKR} {ddKR}, {hhKR}{ampmKR} {tzKR} '
    if data[1].strftime("%d") == data[0].strftime("%d"):
        hhEU, ampmEU, tzEU = data[1].strftime("%#I").lstrip('0'), data[1].strftime("%p").lower(), data[1].strftime("%Z")
        timeStr += f'( {hhEU}{ampmEU} {tzEU} '
    else:
        mmEU, ddEU, hhEU, ampmEU, tzEU = data[1].strftime("%b"), data[1].strftime("%#d").lstrip('0'), data[1].strftime("%#I").lstrip('0'), data[1].strftime("%p").lower(), data[1].strftime("%Z")
        timeStr += f'( {mmEU} {ddEU}, {hhEU}{ampmEU} {tzEU} '
    if data[2].strftime("%d") == data[0].strftime("%d"):
        hhAM, ampmAM, tzAM = data[2].strftime("%#I").lstrip('0').lstrip('0'), data[2].strftime("%p").lower(), data[2].strftime("%Z")
        timeStr += f'/ {hhAM}{ampmAM} {tzAM} )'
    else:
        mmAM, ddAM, hhAM, ampmAM, tzAM = data[2].strftime("%b"), data[2].strftime("%#d").lstrip('0'), data[2].strftime("%#I").lstrip('0'), data[2].strftime("%p").lower(), data[2].strftime("%Z")
        timeStr += f'/ {mmAM} {ddAM}, {hhAM}{ampmAM} {tzAM} )'
    return timeStr


def get_rsl(data):
    """ Returns Region, Server and/or League information """
    l = data.split('(')[0].strip()
    return l


def get_prize(data):
    """ Returns any prizepool, if any """
    pr = data
    if pr == "":
        pr = None
    elif pr == "-":
        pr = None
    return pr

def get_bracket(dataChallonge, dataBrackets):
    """ Returns the bracket, which is in nearly all cases the signup page as well """
    if dataChallonge:
        return dataChallonge
    elif dataBrackets:
        return dataBrackets
    else:
        return None


def eradicate_comments(data, s=''):
    for ind, com_open in enumerate(data.split('<!--')):
        if ind == 0:
            s += com_open
        if len(com_open.split('-->')) > 1:
            s += com_open.split('-->')[1]
    return s


def steal(dataset: dict):
    events = [[], [], []]
    for ind, key in enumerate(dataset.keys()):
        data = eradicate_comments(dataset[key])
        dataSplit = data.split('User:(16thSq) Kuro/')
        if 'This=1' in dataSplit[3].split('}}')[0]:
            evLst = list()
            for i in range(4, len(dataSplit)):
                evDct = dict()
                for j, k in enumerate(dataSplit[i].split('|')):
                    k = k.replace('<br>', ' ').replace('  ', ' ').strip()
                    if 0 < j < 17:
                        if len(k.split('=')) == 2:
                            evDct[k.split('=')[0]] = k.split('=')[1]
                evLst.append(evDct)

        elif 'This=2' in dataSplit[3].split('}}')[0]:
            evLst = list()
            for i in range(4, len(dataSplit)):
                evDct = dict()
                for j, k in enumerate(dataSplit[i].split('|')):
                    k = k.replace('<br>',' ').replace('  ',' ').strip()
                    if 0 < j < 17:
                        #print(k)
                        if len(k.split('=')) == 2:
                            evDct[k.split('=')[0]] = k.split('=')[1]
                evLst.append(evDct)

        elif 'This=3' in dataSplit[3].split('}}')[0]:
            evLst = list()

        l = list()
        for evLstItem in evLst:
            countdown = get_cd(evLstItem['deadline'].strip())
            date = get_time(evLstItem['date'].strip())
            mode = evLstItem['mode'].strip()
            name = evLstItem['event'].strip()
            try:
                region, server = evLstItem['region'].strip(), evLstItem['server'].strip()
                league = get_rsl(evLstItem['league'].strip())
            except:
                region, server = evLstItem['region'].strip(), evLstItem['server'].strip()
                league = ''
            try:
                prize = get_prize(evLstItem['prizepool'].strip())
            except:
                prize = None
            try:
                matcherino = evLstItem['matcherino'].strip()
            except:
                matcherino = None
            try:
                matcherinoCode = evLstItem['coupon'].strip()
            except:
                matcherinoCode = None
            try:
                bracket = get_bracket(evLstItem['challonge'].strip(), evLstItem['brackets'].strip())
            except:
                bracket = evLst[i]['challonge'].strip()
            events[ind].append([name, date, region, league, server, prize, matcherino, matcherinoCode, bracket, countdown, mode])
    return events
