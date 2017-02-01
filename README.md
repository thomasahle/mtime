# mtime

Script for managing mtime by the terminal.

    > python3 mtime.py --username thdy --show-table --date 2017-1-1
    Password: [type password]
    Connecting...
    Getting Schema for 2017-1-1...

    1001 - General work/Generel arbejde AliasId: 165
    8226 - Scalable Similarity Search AliasId: 214
    90006 - Illness/Sygdom AliasId: 13

                 1001:165  8226:214  90006:13
      2017-1-1 H
      2017-1-1       1,70      7,40
      2017-1-1       1,70      6,00
      2017-1-1       2,90      7,40
      2017-1-1       1,60      6,10
      2017-1-1       3,40      5,80
      2017-1-1 W
      2017-1-1 W
      2017-1-1       2,20      5,60
      2017-1-1       3,50      5,80
      2017-1-1       0,40      6,10
      2017-1-1       3,60      5,70
      2017-1-1       5,00      7,70
      2017-1-1 W
      2017-1-1 W
      2017-1-1       0,20      4,60
      2017-1-1       0,50      6,50
      2017-1-1       0,20      7,10
      2017-1-1       0,60      5,10
      2017-1-1       0,80      5,80
      2017-1-1 W
      2017-1-1 W
      2017-1-1       1,20      5,10
      2017-1-1       3,20      4,30
      2017-1-1       0,70      9,20
      2017-1-1       2,40      3,30
      2017-1-1       2,80      7,30
      2017-1-1 W
      2017-1-1 W
      2017-1-1       4,70      5,50
      2017-1-1       3,80      4,90

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
                    [--update UPDATE] [--approve [COMMENT]] [--show-accounts]
                    [--show-table]

    Script for managing mtime by the terminal.

    optional arguments:
      -h, --help           show this help message and exit
      --username USERNAME  From your email, such as pagh. Dont use @itu.dk.
      --password PASSWORD  Your mtime password. Ignore this if you don't want your
                           password in your shell history.
      --date DATE          The date you want to access, such as 2017-12-31.
                           Defaults to today, 2017-2-1.
      --update UPDATE      Use with the value account:alias:hours, such as
                           8000:100:2,4, to update account 8000 to 2,4 hours for
                           the given date.
      --approve [COMMENT]  Approves the month. Can't be undone. Unless it fails.
                           The comment is optional.
      --show-accounts      Prints a list of your possible accounts.
      --show-table         Prints a table of your work this month.
