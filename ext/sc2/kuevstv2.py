from datetime import datetime
import pytz


def get_cd(data):
    """ Returns the countdown of the event
    e.g. event sign up ends on 10:00 on November 4th
    currently is 03:00, November 3rd
    returns: datetime object with the following info
    +1day7hours
    """
    cdTime = datetime.strptime(f'{data} +0900',
                                '%B %d, %Y - %H:%M {{Abbr/KST}} %z')
    curTime = datetime.now(tz=pytz.timezone('Asia/Seoul'))
    return cdTime - curTime


def time_to_times(data):
    """ Returns the event date for 3 timeszones """
    timeKR = pytz.timezone('Asia/Seoul').localize(data)
    timeAM = timeKR.astimezone(pytz.timezone('PST8PDT'))
    timeEU = timeKR.astimezone(pytz.timezone('Europe/Berlin'))
    return timeKR, timeEU, timeAM


def times_to_string(data):
    """ Returns beautiful date data """
    mmKR = data[0].strftime("%B")
    ddKR = data[0].strftime("%#d").lstrip('0')
    hhKR = data[0].strftime("%#I").lstrip('0')
    ampmKR = data[0].strftime("%p").lower()
    tzKR = data[0].strftime("%Z")
    timeStr = f'{mmKR} {ddKR}, {hhKR}{ampmKR} {tzKR} '

    if data[1].strftime("%d") == data[0].strftime("%d"):
        hhEU = data[1].strftime("%#I").lstrip('0')
        ampmEU = data[1].strftime("%p").lower()
        tzEU = data[1].strftime("%Z")
        timeStr += f'( {hhEU}{ampmEU} {tzEU} '
    else:
        mmEU = data[1].strftime("%b")
        ddEU = data[1].strftime("%#d").lstrip('0')
        hhEU = data[1].strftime("%#I").lstrip('0')
        ampmEU = data[1].strftime("%p").lower()
        tzEU = data[1].strftime("%Z")
        timeStr += f'( {mmEU} {ddEU}, {hhEU}{ampmEU} {tzEU} '
    if data[2].strftime("%d") == data[0].strftime("%d"):
        hhAM = data[2].strftime("%#I").lstrip('0').lstrip('0')
        ampmAM = data[2].strftime("%p").lower()
        tzAM = data[2].strftime("%Z")
        timeStr += f'/ {hhAM}{ampmAM} {tzAM} )'
    else:
        mmAM = data[2].strftime("%b")
        ddAM = data[2].strftime("%#d").lstrip('0')
        hhAM = data[2].strftime("%#I").lstrip('0')
        ampmAM = data[2].strftime("%p").lower()
        tzAM = data[2].strftime("%Z")
        timeStr += f'/ {mmAM} {ddAM}, {hhAM}{ampmAM} {tzAM} )'
    return timeStr


def times_to_string24(data):
    """ Returns beautiful date data """
    mmKR = data[0].strftime("%B")
    ddKR = data[0].strftime("%#d").lstrip('0')
    hhKR = data[0].strftime("%#H").lstrip('0')
    if not hhKR:
        hhKR = '0'
    tzKR = data[0].strftime("%Z")
    timeStr = f'{mmKR} {ddKR}, {hhKR}h {tzKR} '

    if data[1].strftime("%d") == data[0].strftime("%d"):
        hhEU = data[1].strftime("%#H").lstrip('0')
        tzEU = data[1].strftime("%Z")
        timeStr += f'( {hhEU}h {tzEU} '
    else:
        mmEU = data[1].strftime("%b")
        ddEU = data[1].strftime("%#d").lstrip('0')
        hhEU = data[1].strftime("%#H").lstrip('0')
        tzEU = data[1].strftime("%Z")
        timeStr += f'( {mmEU} {ddEU}, {hhEU}h {tzEU} '
    if data[2].strftime("%d") == data[0].strftime("%d"):
        hhAM = data[2].strftime("%#H").lstrip('0').lstrip('0')
        tzAM = data[2].strftime("%Z")
        timeStr += f'/ {hhAM}h {tzAM} )'
    else:
        mmAM = data[2].strftime("%b")
        ddAM = data[2].strftime("%#d").lstrip('0')
        hhAM = data[2].strftime("%#H").lstrip('0')
        tzAM = data[2].strftime("%Z")
        timeStr += f'/ {mmAM} {ddAM}, {hhAM}h {tzAM} )'
    return timeStr


def get_time(data):
    """ Returns the start date of the event """
    evTime = datetime.strptime(data, '%B %d, %Y - %H:%M {{Abbr/KST}}')
    allTimes = time_to_times(evTime)
    evTimeStr = times_to_string(allTimes)
    return evTimeStr


def get_time24(data):
    """ Return the start date of the event in 24h format """
    evTime = datetime.strptime(data, '%B %d, %Y - %H:%M {{Abbr/KST}}')
    allTimes = time_to_times(evTime)
    evTimeStr = times_to_string24(allTimes)
    return evTimeStr


def get_rsl(data):
    """ Returns Region, Server and/or League information """
    lg = data.split('(')[0].strip()
    return lg


def get_prize(data):
    """ Returns any prizepool, if any """
    pr = data
    if pr == "":
        pr = None
    elif pr == "-":
        pr = None
    return pr

def get_bracket(dataChallonge, dataBrackets):
    """ Returns the bracket, which is in most cases the signup page too """
    if dataChallonge:
        return dataChallonge
    elif dataBrackets:
        return dataBrackets
    else:
        return None


def eradicate_comments(data, s=''):
    for ind, comOpen in enumerate(data.split('<!--')):
        if ind == 0:
            s += comOpen
        if len(comOpen.split('-->')) > 1:
            s += comOpen.split('-->')[1]
    return s

def get_list(data):
    evLst = list()
    for i in range(4, len(data)):
        evDct = dict()
        for j, k in enumerate(data[i].split('|')):
            k = k.replace('<br>', ' ').replace('  ', ' ').strip()
            if 0 < j < 17:
                if len(k.split('=')) == 2:
                    evDct[k.split('=')[0]] = k.split('=')[1]
        evLst.append(evDct)
    return evLst

def steal(dataset: dict):
    events = [[], [], []]
    for ind, key in enumerate(dataset.keys()):
        data = eradicate_comments(dataset[key])
        dataSplit = data.split('User:(16thSq) Kuro/')
        if 'This=1' in dataSplit[3].split('}}')[0]:
            evLst = get_list(dataSplit)
        elif 'This=2' in dataSplit[3].split('}}')[0]:
            evLst = get_list(dataSplit)
        elif 'This=3' in dataSplit[3].split('}}')[0]:
            evLst = list()

        for evLstItem in evLst:
            try:
                countdown = get_cd(evLstItem['deadline'].strip())
            except:
                countdown = None
            try:
                date = get_time(evLstItem['date'].strip())
            except:
                date = None
            if not date:
                try:
                    _tmpData = evLstItem['date'].strip()
                    _tmpDate = datetime.strptime(_tmpData, '%B %d, %Y - %H:%M {{Abbr/KST}}')
                    _tmpMm = _tmpDate[0].strftime("%B")
                    _tmpDd = _tmpDate[0].strftime("%#d").lstrip('0')
                    date = f'{_tmpMm} {_tmpDd}'
                except:
                    pass
            try:
                date24 = get_time24(evLstItem['date'].strip())
            except:
                date24 = None
            if not date24:
                try:
                    _tmpData = evLstItem['date'].strip()
                    _tmpDate = datetime.strptime(_tmpData, '%B %d, %Y - %H:%M {{Abbr/KST}}')
                    _tmpMm = _tmpDate[0].strftime("%B")
                    _tmpDd = _tmpDate[0].strftime("%#d").lstrip('0')
                    date24 = f'{_tmpMm} {_tmpDd}'
                except:
                    pass
            try:
                mode = evLstItem['mode'].strip()
            except:
                mode = None
            try:
                name = evLstItem['event'].strip()
            except:
                name = None
            try:
                region = evLstItem['region'].strip()
                server = evLstItem['server'].strip()
                league = get_rsl(evLstItem['league'].strip())
            except:
                region = evLstItem['region'].strip()
                server = evLstItem['server'].strip()
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
                matcherinoCode = ''
            try:
                bracket = get_bracket(evLstItem['challonge'].strip(),
                                      evLstItem['brackets'].strip())
            except:
                bracket = evLstItem['challonge'].strip()
            events[ind].append({
                'name': name,
                'date12': date,
                'date24': date24,
                'region': region,
                'league': league,
                'server': server,
                'prize': prize,
                'matLink': matcherino,
                'matCode': matcherinoCode,
                'grid': bracket,
                'cd': countdown,
                'mode': mode
            })
    return events
