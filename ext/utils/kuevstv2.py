from datetime import datetime
import pytz


def get_cd(data):
    """ Returns the countdown of the event
    e.g. event sign up ends on 10:00 on November 4th
    currently is 03:00, November 3rd
    returns: datetime object with the following info
    +1day7hours
    """
    countdown_time = datetime.strptime(f"{data} +0900", "%B %d, %Y - %H:%M {{Abbr/KST}} %z")
    current_time = datetime.now(tz=pytz.timezone('Asia/Seoul'))
    return countdown_time - current_time


def time_to_times(data):
    """ Returns the event date for 3 timezones """
    time_kr = pytz.timezone('Asia/Seoul').localize(data)
    time_am = time_kr.astimezone(pytz.timezone('PST8PDT'))
    time_eu = time_kr.astimezone(pytz.timezone('Europe/Berlin'))
    return time_kr, time_eu, time_am


def times_to_string(data):
    """ Returns beautiful date data """
    month_kr = data[0].strftime('%B')
    day_kr = data[0].strftime('%#d').lstrip('0')
    hours_kr = data[0].strftime('%#I').lstrip('0')
    ampm_kr = data[0].strftime('%p').lower()
    timezone_kr = data[0].strftime('%Z')
    time_str = f"{month_kr} {day_kr}, {hours_kr}{ampm_kr} {timezone_kr} "

    if data[1].strftime('%d') == data[0].strftime('%d'):
        hours_eu = data[1].strftime('%#I').lstrip('0')
        ampm_eu = data[1].strftime('%p').lower()
        timezone_eu = data[1].strftime('%Z')
        time_str += f"( {hours_eu}{ampm_eu} {timezone_eu} "
    else:
        month_eu = data[1].strftime('%b')
        day_eu = data[1].strftime('%#d').lstrip('0')
        hours_eu = data[1].strftime('%#I').lstrip('0')
        ampm_eu = data[1].strftime('%p').lower()
        timezone_eu = data[1].strftime('%Z')
        time_str += f"( {month_eu} {day_eu}, {hours_eu}{ampm_eu} {timezone_eu} "
    if data[2].strftime('%d') == data[0].strftime('%d'):
        hours_am = data[2].strftime('%#I').lstrip('0').lstrip('0')
        ampm_am = data[2].strftime('%p').lower()
        timezone_am = data[2].strftime('%Z')
        time_str += f"/ {hours_am}{ampm_am} {timezone_am} )"
    else:
        month_am = data[2].strftime('%b')
        day_am = data[2].strftime('%#d').lstrip('0')
        hours_am = data[2].strftime('%#I').lstrip('0')
        ampm_am = data[2].strftime('%p').lower()
        timezone_am = data[2].strftime('%Z')
        time_str += f"/ {month_am} {day_am}, {hours_am}{ampm_am} {timezone_am} )"
    return time_str


def times_to_string24(data):
    """ Returns beautiful date data """
    month_kr = data[0].strftime('%B')
    day_kr = data[0].strftime('%#d').lstrip('0')
    hours_kr = data[0].strftime('%#H').lstrip('0')
    if not hours_kr:
        hours_kr = '0'
    timezone_kr = data[0].strftime('%Z')
    time_str = f"{month_kr} {day_kr}, {hours_kr}h {timezone_kr} "

    if data[1].strftime('%d') == data[0].strftime('%d'):
        hours_eu = data[1].strftime('%#H').lstrip('0')
        timezone_eu = data[1].strftime('%Z')
        time_str += f"( {hours_eu}h {timezone_eu} "
    else:
        month_eu = data[1].strftime('%b')
        day_eu = data[1].strftime('%#d').lstrip('0')
        hours_eu = data[1].strftime('%#H').lstrip('0')
        timezone_eu = data[1].strftime('%Z')
        time_str += f"( {month_eu} {day_eu}, {hours_eu}h {timezone_eu} "
    if data[2].strftime('%d') == data[0].strftime('%d'):
        hours_am = data[2].strftime('%#H').lstrip('0').lstrip('0')
        timezone_am = data[2].strftime('%Z')
        time_str += f"/ {hours_am}h {timezone_am} )"
    else:
        month_am = data[2].strftime('%b')
        day_am = data[2].strftime('%#d').lstrip('0')
        hours_am = data[2].strftime('%#H').lstrip('0')
        timezone_am = data[2].strftime('%Z')
        time_str += f"/ {month_am} {day_am}, {hours_am}h {timezone_am} )"
    return time_str


def get_time(data):
    """ Returns the start date of the event """
    event_datetime = datetime.strptime(data, '%B %d, %Y - %H:%M {{Abbr/KST}}')
    all_datetime = time_to_times(event_datetime)
    event_datetime_string = times_to_string(all_datetime)
    return event_datetime_string


def get_time24(data):
    """ Return the start date of the event in 24h format """
    event_datetime = datetime.strptime(data, '%B %d, %Y - %H:%M {{Abbr/KST}}')
    all_datetime = time_to_times(event_datetime)
    event_datetime_string = times_to_string24(all_datetime)
    return event_datetime_string


def get_league(data):
    """ Returns Region, Server and/or League information """
    league = data.split('(')[0].strip()
    return league


def get_prize(data):
    """ Returns any prizepool, if any """
    pr = data
    if pr == '':
        pr = ''
    elif pr == '-':
        pr = ''
    return pr


def get_bracket(data_challonge, data_brackets):
    """ Returns the bracket, which is in most cases the signup page too """
    if data_challonge:
        return data_challonge
    elif data_brackets:
        return data_brackets
    else:
        return ''


def eradicate_comments(data, s=''):
    for ind, comOpen in enumerate(data.split('<!--')):
        if ind == 0:
            s += comOpen
        if len(comOpen.split('-->')) > 1:
            s += comOpen.split('-->')[1]
    return s


def get_list(data):
    event_list = list()
    for i in range(4, len(data)):
        event_info = dict()
        for j, k in enumerate(data[i].split('|')):
            k = k.replace('<br>', ' ').replace('  ', ' ').strip()
            if 0 < j < 17:
                if len(k.split('=')) == 2:
                    event_info[k.split('=')[0]] = k.split('=')[1]
        event_list.append(event_info)
    return event_list


def steal(data_set: dict):
    events = [[], [], []]
    for ind, key in enumerate(data_set.keys()):
        data = eradicate_comments(data_set[key])
        data_split = data.split('User:(16thSq) Kuro/')
        if 'This=1' in data_split[3].split('}}')[0]:
            event_list = get_list(data_split)
        elif 'This=2' in data_split[3].split('}}')[0]:
            event_list = get_list(data_split)
        elif 'This=3' in data_split[3].split('}}')[0]:
            event_list = list()
        else:
            event_list = list()

        for event in event_list:
            try:
                countdown = get_cd(event['deadline'].strip())
            except:
                countdown = ''
            try:
                date = get_time(event['date'].strip())
            except:
                date = ''
            if not date:
                try:
                    tmp_data = event['date'].strip()
                    tmp_date = datetime.strptime(tmp_data, '%B %d, %Y - %H:%M {{Abbr/KST}}')
                    tmp_month = tmp_date[0].strftime('%B')
                    tmp_day = tmp_date[0].strftime('%#d').lstrip('0')
                    date = f"{tmp_month} {tmp_day}"
                except:
                    pass
            try:
                date24 = get_time24(event['date'].strip())
            except:
                date24 = ''
            if not date24:
                try:
                    tmp_data = event['date'].strip()
                    tmp_date = datetime.strptime(tmp_data, '%B %d, %Y - %H:%M {{Abbr/KST}}')
                    tmp_month = tmp_date[0].strftime('%B')
                    tmp_day = tmp_date[0].strftime('%#d').lstrip('0')
                    date24 = f"{tmp_month} {tmp_day}"
                except:
                    pass
            try:
                mode = event['mode'].strip()
            except:
                mode = ''
            try:
                name = event['event'].strip()
            except:
                name = ''
            try:
                region = event['region'].strip()
                server = event['server'].strip()
                league = get_league(event['league'].strip())
                if league == 'Online':
                    league = ''
            except:
                region = event['region'].strip()
                server = event['server'].strip()
                league = ''
            try:
                prize = get_prize(event['prizepool'].strip())
            except:
                prize = ''
            try:
                matcherino = event['matcherino'].strip()
            except:
                matcherino = ''
            try:
                matcherino_code = event['coupon'].strip()
            except:
                matcherino_code = ''
            try:
                bracket = get_bracket(event['challonge'].strip(),
                                      event['brackets'].strip())
            except:
                bracket = event['challonge'].strip()
            events[ind].append({
                'name': name,
                'date12': date,
                'date24': date24,
                'region': region,
                'league': league,
                'server': server,
                'prize': prize,
                'matLink': matcherino,
                'matCode': matcherino_code,
                'bracket': bracket,
                'cd': countdown,
                'mode': mode
            })
    return events
