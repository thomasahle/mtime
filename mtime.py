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

class MTime:
    def __init__(self):
        self.session = requests.Session()
    def __enter__(self):
        self.session.__enter__()
        return self
    def __exit__(self, *args):
        self.session.__exit__(*args)

    def connect(self, user):
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
                year, month, day, aliasid = td.div.input.attrs['id'].split('_')
                date = datetime.date(int(year), int(month), int(day))
                hours = td.div.input.attrs['value']
                if 'wday' in td.attrs['class']:
                    day_type = WDAY
                elif 'hday' in td.attrs['class']:
                    day_type = HDAY
                else: day_type = NDAY
                enabled = 'enabled' in td.attrs['class']
                days.append(Day(date, enabled, day_type, hours))
            table.append((account, days))
        return r.status_code, table

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
            print(' '*12, end=' ')
            for acc, _ in table:
                print(acc.text, end='; ')
            print()
            for row in zip(*[vals for acc, vals in table]):
                main_day = row[0]
                print(formatDate(main_day.date, 'ymd').rjust(10), end=' ')
                if main_day.type == HDAY: print('H', end=' ')
                elif main_day.type == WDAY: print('W', end=' ')
                else: print(' ', end=' ')
                for i, day in enumerate(row):
                    print(day.hours.rjust(len(table[i][0].text)), end='  ')
                print()

if __name__ == '__main__':
    try:
        main()
    except requests.exceptions.ConnectionError as e:
        print('Problems connecting', e)

