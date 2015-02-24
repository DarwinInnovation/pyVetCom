'''
Created on 3 May 2013

@author: richardm
'''
__author__ = 'richardm'

import datetime

class DayTotal(object):
    def __init__(self, type, name, dir):
        self._type = type
        self._name = name
        self._dir  = dir
        self._exvat = 0
        self._incvat = 0
        self._vat = 0

        self._count = 0

    def add(self, sldoc):
        if type(sldoc) is DayTotal:
            self._exvat += sldoc._exvat
            self._incvat += sldoc._incvat
            self._vat += sldoc._vat
            self._count += sldoc._count
            return

        if sldoc.TYPE <> self._type:
            assert 'Wrong type'
        self._exvat += sldoc.AMOUNT * self._dir
        self._incvat += sldoc.TOTAL * self._dir
        self._vat += (sldoc.VAT  * self._dir) or 0

        self._count += 1

    def getTableRow(self, mult):
        mult = mult or 1
        return [self._name,
                "&pound;%.2f"%(self._incvat*mult),
                self._count,
                "&pound;%.2f"%(self._exvat*mult)]

    def __str__(self):
        return "%7.2f (%d)"%(self._incvat, self._count)


class DayFigures(object):
    _type_descriptions = [
        'Invoice', 'Credit Note',
        'Cash', 'Cheque', 'Credit Card', 'Credit Transfer',
         'Journal Debit', 'Journal Credit'
    ]

    _type_credit_or_debit = [
        -1, 1,
        1, 1, 1, 1,
        -1, 1
    ]

    def __init__(self, dt):
        self._date = dt
        self._totals = []
        for t in range(0,8):
            self._totals.append(DayTotal(t, DayFigures._type_descriptions[t], DayFigures._type_credit_or_debit[t]))

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

    def get_table(self, min_type, max_type, mult):
        mult = mult or 1

        table = []
        total = DayTotal(0, "TOTAL", 1)
        for t in range(min_type, max_type):
            total.add(self._totals[t])
            table.append(self._totals[t].getTableRow(mult))
        table.append(total.getTableRow(mult))
        return table

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


