# mtime

Script for managing mtime by the terminal.

    > python3 mtime.py --username=thdy --password=hemmelig --show-table
    Connecting...
    Getting Schema for 2017-1-23...
                 1001 - General work/Generel arbejde; 8226 - Scalable Similarity Search; 90006 - Illness/Sygdom;
      2017-1-1 H
      2017-1-2                                  2,00                               6,00
      2017-1-3                                  2,00                               2,00
      2017-1-4                                  2,00
      2017-1-5
      2017-1-6
      2017-1-7 W
      2017-1-8 W
      2017-1-9
     2017-1-10
     2017-1-11
     2017-1-12
     2017-1-13
     2017-1-14 W
     2017-1-15 W
     2017-1-16
     2017-1-17
     2017-1-18
     2017-1-19
     2017-1-20
     2017-1-21 W
     2017-1-22 W
     2017-1-23                                  2,40
     2017-1-24
     2017-1-25
     2017-1-26
     2017-1-27
     2017-1-28 W
     2017-1-29 W
     2017-1-30
     2017-1-31

To update your entries, first get your list of accounts and aliasId's:

    > python3 mtime.py --username=thdy --password=hemmelig --show-accounts
    Connecting...
    Getting Schema for 2017-1-23...
    1001 - General work/Generel arbejde AliasId: 165
    8226 - Scalable Similarity Search AliasId: 214
    90006 - Illness/Sygdom AliasId: 13

And then simply call update:

    > python3 mtime.py --username=thdy --password=hemmelig --update=1001:165:6
    Connecting...
    Updated 1001 on 2017-1-23 to 6 hours

The full list of arguments:

    > python3 mtime.py --help
    usage: mtime.py [-h] [--username USERNAME] [--password PASSWORD] [--date DATE]
                    [--update UPDATE] [--show-accounts] [--show-table]

    Script for managing mtime by the terminal.

    optional arguments:
      -h, --help           show this help message and exit
      --username USERNAME  From your email, such as pagh. Dont use @itu.dk.
      --password PASSWORD  Your mtime password.
      --date DATE          The date you want to access, such as 2017-12-31.
                           Defaults to today, 2017-1-23.
      --update UPDATE      Use with the value account:alias:hours, such as
                           8000:100:2,4, to update account 8000 to 2,4 hours for
                           the given date.
      --show-accounts      Prints a list of your possible accounts.
      --show-table         Prints a table of your work this month.
