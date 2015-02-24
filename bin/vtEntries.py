#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

__author__ = 'richardm'

import logging
import sys
from pyVetCom import *
from datetime import date, timedelta


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    vc = PyVetCom.PyVetCom("192.168.3.200")

    start = date.today() - timedelta(weeks=1)
    while start.weekday() <> 0:
        start = start - timedelta(days=1)
    end = date.today() - timedelta(days=1)

    dailyfigures = []

    type_accs = {
            2: {'acc':   'Customers: 2015 Cash', 'details': 'VW Cash'},
            3: {'acc':   'Customers: 2015 Cash', 'details': 'VW Cheques'},
            4: {'acc': 'Customers: 2015 C Card', 'details': 'VW Credit Card'},
            5: {'acc':   'Customers: 2015 BACS', 'details': 'VW Bank Transfers'},
            6: {'acc':  'Customers: 2015 Error', 'details': 'VW Journal Debit'},
            7: {'acc':  'Customers: 2015 Error', 'details': 'VW Journal Credit'},
        }

    ofile = open('vt.csv', 'w')

    day = start
    while day < end:
        wd = day.weekday()

        df = DayFigures.DayFigures(day)
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
