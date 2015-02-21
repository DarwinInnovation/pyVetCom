__author__ = 'richardm'

from pyVetCom import *
from datetime import date, timedelta


if __name__ == '__main__':
   # logging.basicConfig(level=logging.DEBUG)

    vc = PyVetCom.PyVetCom("192.168.3.200")

    day = date.today()

    df = DayFigures.DayFigures(day)
    df.get(vc)

    tables = [(0,2), (2, 6), (6, 8)]

    print 'Status: 200 OK'
    print 'Content-type: text/html\r\n'
    print

    print '<HTML><HEAD><TITLE>Day Summary</TITLE></HEAD>'
    print '<BODY>'
    print '<H1>%s</H1>'%day.strftime("%a %d/%m/%y")

    print '<br>'
    for t in tables:
        table = df.get_table(t[0], t[1])

        print '<TABLE>'
        for r in table:
            print '<TR>'
            for c in r:
                print '<TD>%s</TD>'%c
            print '</TR>'
        print '</TABLE>'
    print '</BODY>'
