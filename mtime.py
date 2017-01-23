# You need some packages to run this.
# pip3 install ntlm-auth requests requests-ntlm bs4

import argparse
import collections
import datetime
import requests
from bs4 import BeautifulSoup
from requests_ntlm import HttpNtlmAuth

User = collections.namedtuple('User', 'username, password')
Account = collections.namedtuple('Account', 'text, accountNo, aliasId')
Day = collections.namedtuple('Day', 'date, enabled, type')
HDAY, WDAY, NDAY = range(3)

#GEN_ACC = Account('General', 1001, 165)
#SSS_ACC = Account('SSS', 8226, 214)

def connectSession(session, user):
    print('Connecting...')
    session.auth = HttpNtlmAuth('itu\\'+ user.username, user.password, session)
    return session.get('https://mtime.itu.dk/')

def formatDate(date, kind):
    if kind == 'ymd': return '{}-{}-{}'.format(date.year, date.month, date.day)
    if kind == 'mdy': return '{}-{}-{}'.format(date.month, date.day, date.year)
    if kind == 'dmy': return '{}-{}-{}'.format(date.day, date.month, date.year)
def parseDate(string, kind):
    a, b, c = map(int, string.split('-'))
    if kind == 'ymd': return datetime.date(a, b, c)
    if kind == 'mdy': return datetime.date(c, a, b)

def sendUpdate (user, date, account, hours):
    with requests.Session() as session:
        r = connectSession(session, user)
        if r.status_code != 200:
            return r.status_code
        soup = BeautifulSoup(r.text, 'html.parser')
        form = {
            'activeUserId': -1,
            'hourHundredths': 'true',
            'tranverseActivityID': '',
            'year': date.year,
            'month': date.month,
            'day': date.day,
            'aliasId': account.aliasId,
            'accountNo': account.accountNo,
            'hours': hours
        }
        r = session.post('https://mtime.itu.dk/Registration/Schema/SaveData', data=form)
        return r.status_code

def getTable(user, date):
    with requests.Session() as session:
        r = connectSession(session, user)
        if r.status_code != 200:
            return r.status_code, []
        print('Getting Schema for {}...'.format(formatDate(date, 'ymd')))
        form = { 'selectedDate': formatDate(date, 'dmy') }
        r = session.get('https://mtime.itu.dk/Registration/Schema/Schema', params=form)
        if r.status_code != 200:
            return r.status_code, []
        soup = BeautifulSoup(r.text, 'html.parser')
        table = []
        for tr in soup.div.table.tbody.find_all('tr'):
            if not 'edit' in tr.attrs['class']:
                continue
            account = Account(tr.td.text.strip(),
                    tr.attrs['data-account-number'],
                    tr.attrs['data-alias-id'])
            days = []
            for td in tr.find_all('td'):
                if not 'data' in td.attrs['class']:
                    continue
                year, month, day, aliasid = td.div.input.attrs['id'].split('_')
                date = datetime.date(int(year), int(month), int(day))
                hours = td.div.input.attrs['value']
                if 'wday' in td.attrs['class']:
                    day_type = WDAY
                elif 'hday' in td.attrs['class']:
                    day_type = HDAY
                else: day_type = NDAY
                enabled = 'enabled' in td.attrs['class']
                days.append((Day(date, enabled, day_type), hours))
            table.append((account, days))
        return r.status_code, table
    return -1, []

def main():
    parser = argparse.ArgumentParser(description='Script for managing mtime by the terminal.')

    parser.add_argument('--username', type=str, help='From your email, such as pagh. Dont use @itu.dk.')
    parser.add_argument('--password', type=str, help='Your mtime password.')

    defdate = formatDate(datetime.date.today(), 'ymd')
    parser.add_argument('--date', type=str, help='The date you want to access, such as 2017-12-31.\
            Defaults to today, {}.'.format(defdate), default=defdate)

    parser.add_argument('--update', type=str, help='Use with the value account:alias:hours, \
            such as 8000:100:2,4, to update account 8000 to 2,4 hours for the given date.')

    parser.add_argument('--show-accounts', action='store_true', help='Prints a list of your possible accounts.')
    parser.add_argument('--show-table', action='store_true', help='Prints a table of your work this month.')

    args = parser.parse_args()


    username = args.username
    password = args.password
    user = User(username, password)
    date = parseDate(args.date, 'ymd')

    if args.update:
        accountNo, aliasId, hours = args.update.split(':')
        account = Account('', accountNo, aliasId)
        err = sendUpdate (user, date, account, hours)
        assert err == 200, 'Updating failed'
        print('Updated {} on {} to {} hours'.format(accountNo, formatDate(date, 'ymd'), hours))

    if args.show_accounts:
        err, table = getTable(user, date)
        assert err == 200, 'Getting the table failed'
        for acc, vals in table:
            print(acc.text, 'AliasId:', acc.aliasId)

    if args.show_table:
        err, table = getTable(user, date)
        assert err == 200, 'Getting the table failed'
        print(' '*12, end=' ')
        for acc, _ in table:
            print(acc.text, end='; ')
        print()
        for row in zip(*[vals for acc, vals in table]):
            day = row[0][0]
            print(formatDate(day.date, 'ymd').rjust(10), end=' ')
            if day.type == HDAY: print('H', end=' ')
            elif day.type == WDAY: print('W', end=' ')
            else: print(' ', end=' ')
            for i, (_, hours) in enumerate(row):
                print(hours.rjust(len(table[i][0].text)), end='  ')
            print()

if __name__ == '__main__':
    main()
