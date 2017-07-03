# You need some packages to run this.
# pip3 install ntlm-auth requests requests-ntlm bs4

import argparse
import collections
import datetime
import getpass
import requests
import time
from bs4 import BeautifulSoup
from requests_ntlm import HttpNtlmAuth

User = collections.namedtuple('User', 'username, password')
Account = collections.namedtuple('Account', 'text, accountNo, aliasId')
Day = collections.namedtuple('Day', 'date, enabled, type, hours')
HDAY, WDAY, NDAY = range(3)

def formatDate(date, kind):
    if kind == 'ymd': return '{}-{}-{}'.format(date.year, date.month, date.day)
    if kind == 'mdy': return '{}-{}-{}'.format(date.month, date.day, date.year)
    if kind == 'dmy': return '{}-{}-{}'.format(date.day, date.month, date.year)
def parseDate(string, kind):
    a, b, c = map(int, string.split('-'))
    if kind == 'ymd': return datetime.date(a, b, c)
    if kind == 'mdy': return datetime.date(c, a, b)
    if kind == 'dmy': return datetime.date(c, b, a)

class MTime:
    def __init__(self):
        self.session = requests.Session()
    def __enter__(self):
        self.session.__enter__()
        return self
    def __exit__(self, *args):
        self.session.__exit__(*args)

    def connect(self, user):
        self.user = user
        self.session.auth = HttpNtlmAuth(
                'itu\\'+ user.username, user.password, self.session)
        return self.session.get('https://mtime.itu.dk/')

    def sendUpdate (self, date, account, hours):
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
        url = 'https://mtime.itu.dk/Registration/Schema/SaveData'
        r = self.session.post(url, data=form)
        return r.status_code

    def getTable(self, date):
        form = { 'selectedDate': formatDate(date, 'dmy') }
        url = 'https://mtime.itu.dk/Registration/Schema/Schema'
        r = self.session.get(url, params=form)
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
                day_type = NDAY
                for key, value in (('wday',WDAY), ('hday',HDAY)):
                    if key in td.attrs['class']:
                        day_type = value
                enabled = 'enabled' in td.attrs['class']
                hours = td.div.span.text.strip()
                entry_date = date.replace(day=len(days)+1)
                days.append(Day(entry_date, enabled, day_type, hours))
                # Some tests
                if enabled:
                    assert td.div.input.attrs['id'] == '{}_{}_{}_{}'.format(
                            date.year, date.month, entry_date.day, account.aliasId)
                    assert hours == td.div.input.attrs['value']
            table.append((account, days))
        return r.status_code, table

    def userApprove(self, date, comment=''):
        form = {
            'selectedUser':self.user.username.upper(),
            'canManagerApprove':'false',
            'canUnapprove':'false',
            'managerCheckedById':'',
            'day':'1',
            'month':date.month,
            'year':date.year,
            'autoCalcInfoStr':'',
            'manualTransfer':'',
            'comment':comment,
            'role':'',
            '_':int(time.time()*1000)
        }
        url = 'https://mtime.itu.dk/Summary/Overview/UserApprove'
        r = self.session.post(url, params=form)
        if r.status_code != 200:
            return r.status_code
        return r.status_code

def main():
    parser = argparse.ArgumentParser(description='Script for managing mtime by the terminal.')

    parser.add_argument('--username', type=str, help='From your email, such as pagh. Dont use @itu.dk.')
    parser.add_argument('--password', type=str, help='Your mtime password. Ignore this if you don\'t want your password in your shell history.')

    defdate = formatDate(datetime.date.today(), 'ymd')
    parser.add_argument('--date', type=str, help='The date you want to access, such as 2017-12-31.\
            Defaults to today, {}.'.format(defdate), default=defdate)

    parser.add_argument('--update', type=str, help='Use with the value account:alias:hours, \
            such as 8000:100:2,4, to update account 8000 to 2,4 hours for the given date.')
    parser.add_argument('--approve', type=str, metavar='COMMENT', nargs='?', const='', help='Approves the month. Can\'t be undone. Unless it fails. The comment is optional.')

    parser.add_argument('--show-accounts', action='store_true', help='Prints a list of your possible accounts.')
    parser.add_argument('--show-table', action='store_true', help='Prints a table of your work this month.')

    args = parser.parse_args()

    username = args.username
    if username is None:
        username = input('Username: ')
    password = args.password
    if password is None:
        password = getpass.getpass('Password: ')
    user = User(username, password)
    date = parseDate(args.date, 'ymd')

    with MTime() as m:
        print('Connecting...')
        m.connect(user)

        if args.update:
            accountNo, aliasId, hours = args.update.split(':')
            account = Account('', accountNo, aliasId)
            print('Sending update...')
            err = m.sendUpdate(date, account, hours)
            assert err == 200, 'Updating failed'
            print('Updated {} on {} to {} hours'.format(accountNo, formatDate(date, 'ymd'), hours))

        if args.approve is not None:
            print('Approving with comment "{}"...'.format(args.approve))
            err = m.userApprove(date, comment=args.approve)
            assert err == 200, 'Updating failed'

        if args.show_accounts:
            print('Getting Schema for {}...'.format(formatDate(date, 'ymd')))
            err, table = m.getTable(date)
            assert err == 200, 'Getting the table failed'
            for acc, vals in table:
                print(acc.text, 'AliasId:', acc.aliasId)

        if args.show_table:
            print('Getting Schema for {}...'.format(formatDate(date, 'ymd')))
            err, table = m.getTable(date)
            assert err == 200, 'Getting the table failed'
            print()
            for acc, vals in table:
                print(acc.text, 'AliasId:', acc.aliasId)
            print()
            print(' '*12, end=' ')
            titles = ['{}:{}'.format(a.accountNo, a.aliasId) for a, _ in table]
            for title in titles:
                print(title, end='  ')
            print()
            for row in zip(*[vals for acc, vals in table]):
                main_day = row[0]
                print(formatDate(main_day.date, 'ymd').rjust(10), end=' ')
                if main_day.type == HDAY: print('H', end=' ')
                elif main_day.type == WDAY: print('W', end=' ')
                else: print(' ', end=' ')
                for i, day in enumerate(row):
                    print(day.hours.rjust(len(titles[i])), end='  ')
                print()

if __name__ == '__main__':
    try:
        main()
    except requests.exceptions.ConnectionError as e:
        print('Problems connecting', e)

