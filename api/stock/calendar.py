import datetime
import exchange_calendars as ecal

def find_most_recent_trade_date():
    date = datetime.date.today()

    if datetime.datetime.now().hour < 16:
        date = date - datetime.timedelta(days=1)

    xkrx = ecal.get_calendar("XKRX")
    range = xkrx.sessions_in_range(date - datetime.timedelta(days=7), date)
    date = range[-1]
    most_recent_trade_date = date.strftime('%Y%m%d')

    return date

def print_today():
    date = datetime.date.today()

    print('오늘: ' + date.strftime('%Y%m%d'))

def print_most_recent_trade_date():
    date = find_most_recent_trade_date()

    print('최근 거래일: ' + date.strftime('%Y%m%d'))
