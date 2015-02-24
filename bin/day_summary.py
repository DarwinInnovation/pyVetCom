__author__ = 'richardm'

import sys
from pyVetCom import *
from datetime import date, datetime, timedelta


if __name__ == '__main__':
   # logging.basicConfig(level=logging.DEBUG)

    vc = PyVetCom.PyVetCom("192.168.3.200")

    today = date.today()

    day = today
    if len(sys.argv)>1 and sys.argv[1]<>"":
        arg=sys.argv[1]
        if len(arg)==8:
            day = datetime.strptime(arg, "%d-%m-%y").date()


    df = DayFigures.DayFigures(day)
    df.get(vc)

    tables = [(0, 2, -1), (2, 6, 1), (6, 8, 1)]

    print 'Status: 200 OK'
    print 'Content-type: text/html\r\n'
    print

    print '<HTML><HEAD>'
    print '<TITLE>Day Summary</TITLE>' \
          '<LINK rel="stylesheet" href="style.css">' \
          '</HEAD>'
    print '<BODY>'
    print '<H1 align="center">%s</H1>'%day.strftime("%a %d/%m/%y")

    print '<br>'
    print '<TABLE align="center">'
    for t in tables:
        table = df.get_table(t[0], t[1], t[2])
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

        print '</TR><TR><TD colspan="4">&nbsp;</TD></TR>'
    print '</TABLE>'
    if len(sys.argv):
        print '<pre>%s</pre>'%sys.argv

    day_before = (day - timedelta(days=1))
    day_after = (day + timedelta(days=1))
    if day_after > today:
        day_after = None

    print '<TABLE align="center"><tr>'
    day_before_str = day_before.strftime("%d-%m-%y")
    print '<td align="left"><a href="day_summary.py?%s">%s</a></td>'%(day_before_str,day_before_str)
    if day_after is not None:
        day_after_str = day_after.strftime("%d-%m-%y")
        print '<td align="right"><a href="day_summary.py?%s">%s</a></td>'%(day_after_str,day_after_str)
    else:
        print '<td align="right">Up to date</td>'
    print '</TR></TABLE>'
    print '</BODY>'
