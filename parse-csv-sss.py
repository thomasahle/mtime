# Parses CSV output from HoursTracker export (1 entry per day), and transfers data to mTime
# Usage: python parse-csv-sss.py CSV_FILE

import fileinput, sys, os, getpass, mtime

username = input('Username: ')
pw = getpass.getpass("Password: ")

with mtime.MTime() as m:
    print('Connecting to mtime...')
    m.connect(mtime.User(username, pw))
    print('Reading file input...')
    for line in fileinput.input():
        project, day, _, hours = line.split('","')
        if project == '"ERC':
            date = mtime.parseDate(day, 'ymd')
            print('Updating', day, 'to', hours, 'hours.')
            m.sendUpdate(date, mtime.Account('', '8226', '214'), hours)

