#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

__author__ = 'richardm'

import logging
import sys
import PyVetCom
from datetime import date, timedelta

class DayTotal:
    def __init__(self, type):
        self._type = type

        self._exvat = 0
        self._incvat = 0
        self._vat = 0

        self._count = 0

    def add(self, sldoc):
        if sldoc.TYPE <> self._type:
            assert 'Wrong type'
        self._exvat += sldoc.AMOUNT
        self._incvat += sldoc.TOTAL
        self._vat += sldoc.VAT or 0

        self._count += 1

    def __str__(self):
        return "%7.2f (%d)"%(self._incvat, self._count)

class DayFigures:
    def __init__(self, dt):
        self._date = dt
        self._totals = []
        for t in range(0,8):
            self._totals.append(DayTotal(t))

    def get(self, vc):
        doclist = vc.SLDocs().ondate("DATETIME", self._date).getList()

        for d in doclist:
            self._totals[d.TYPE].add(d)

    def __str__(self):
        s = "Date: %s\n"%(self._date.strftime("%d/%m/%y"))
        for t in range(0,8):
            s += "\t%s\n"%self._totals[t]
        return s

    def vt_inv(self, primary_acc):
        invs=self._totals[0]
        if (invs._incvat <= 0.0):
            return None

        out='SIN,'                                  # Type
        out+='[auto],'                              # Ref no
        out+='%s,'%self._date.strftime("%d/%m/%y")  # Date
        out+='"%s",'%primary_acc                    # Primary account
        out+='"VW Invoices (%d)",'%invs._count         # Details
        out+='%.2f,'%invs._incvat                   # Total
        out+='%.2f,'%invs._vat                      # VAT
        out+='%.2f,'%invs._exvat                    # ex VAT
        out+='"Income: Sales",'                     # Analysis account
        out+=',,\n'
        return out

    def vt_cns(self, primary_acc):
        cns=self._totals[1]
        if (cns._incvat <= 0.0):
            return None

        out='SCR,'                                  # Type
        out+='[auto],'                              # Ref no
        out+='%s,'%self._date.strftime("%d/%m/%y")  # Date
        out+='"%s",'%primary_acc
        out+='"VW Credit Notes (%d)",'%cns._count
        out+='%.2f,'%cns._incvat
        out+='%.2f,'%cns._vat
        out+='%.2f,'%cns._exvat
        out+='"Income: Sales",'
        out+=',,\n'
        return out

    def vt_payments(self, primary_acc, type_map):
        total=0.0
        for t in range(2, 6):
            total += self._totals[t]._exvat

        if total <= 0:
            return None

        out='JRN,[auto],'
        out+='%s,,"%s",,,'%(self._date.strftime("%d/%m/%y"), "Payments")
        out+='%.2f,"%s","%s",""\n'%(-total,primary_acc,"VW Payments Total")

        for t in range(2, 6):
            dt = self._totals[t]
            tm = type_map[t]
            if dt._exvat > 0:
                out +='"","","","","",,,%.2f,"%s","%s",\n'%(dt._exvat,tm['acc'],tm['details'])

        return out

    def vt_journals(self, primary_acc, type_map):
        out = None
        for t in range(6, 8):
            total = self._totals[t]._exvat

            if total <= 0:
                continue

            if out is None:
                out = ''

            tm = type_map[t]
            if 'invert' in tm and tm['invert']:
                total = - total

            out+='JRN,[auto],'
            out+='%s,,"%s",,,'%(self._date.strftime("%d/%m/%y"), tm['details'])
            out+='%.2f,"%s","%s",""\n'%(total,primary_acc, tm['details'])
            out +='"","","","","",,,%.2f,"%s","%s",\n'%(-total,tm['acc'],tm['details'])

        return out




if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    vc = PyVetCom.PyVetCom("192.168.3.200")

    start = date(2015, 1, 1) #date.today() - timedelta(weeks=1)
    # while start.weekday() <> 0:
    #     start = start - timedelta(days=1)
    end = date.today() - timedelta(days=1)

    dailyfigures = []

    type_accs = {
            2: {'acc':   'Customers: 2015 Cash', 'details': 'VW Cash'},
            3: {'acc':   'Customers: 2015 Cash', 'details': 'VW Cheques'},
            4: {'acc': 'Customers: 2015 C Card', 'details': 'VW Credit Card'},
            5: {'acc':   'Customers: 2015 BACS', 'details': 'VW Bank Transfers'},
            6: {'acc':  'Customers: 2015 Error', 'details': 'VW Journal Debit'},
            7: {'acc':  'Customers: 2015 Error', 'details': 'VW Journal Credit', 'invert':True},
        }

    ofile = open('vt.csv', 'w')

    day = start
    while day < end:
        wd = day.weekday()

        df = DayFigures(day)
        df.get(vc)

        inv = df.vt_inv("2015")
        cn = df.vt_cns("2015")
        payments = df.vt_payments("Customers: 2015", type_accs)
        journals = df.vt_journals("Customers: 2015", type_accs)

        if inv is not None:
            ofile.write(inv)
        if cn is not None:
            ofile.write(cn)
        if payments is not None:
            ofile.write(payments)
        if journals is not None:
            ofile.write(journals)

        day += timedelta(days=1)
