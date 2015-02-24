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
    print '<TABLE>'
    for t in tables:
        table = df.get_table(t[0], t[1])
        for r in table:
            halign="left"
            print '<TR>'
            if r[0] == "TOTAL":
                style="<STRONG>"
                endstyle="</STRONG>"
            else:
                style=""
                endstyle=""

            for c in r:
                print '<TD align="%s">%s%s%s</TD>'%(halign, style, c, endstyle)
                halign="right"

            print '</TR>'
    print '</TABLE>'
    print '</BODY>'
