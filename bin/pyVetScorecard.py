'''
Created on 8 Oct 2014

@author: richardm
'''

import logging

from PyVetCom import PyVetCom 
import datetime
import time



if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    vc = PyVetCom("192.168.3.200")
    
    inits=["SJM", "CS", "DF"]
    
#     print "Month,"+",".join(inits)
#     
#     for mnth in range(9):
#         start="2014-%02d-01"%(mnth+1)
#         end="2014-%02d-01"%(mnth+2)
#         
#         vals=[str(mnth+1)]
#         for init in inits:
#             isum = vc.Transactions.Charge().between('DATETIME', start, end).eq('INITS', init).sum('TOTAL')
#             vals.append(str(isum))
#         print ",".join(vals)

    print "Week,"+",".join(inits)
    
    start = datetime.date(2014,01,06)
    wkdelta = datetime.timedelta(weeks=1)
    end   = start+wkdelta
    
    for wk in range(51):
        vals=[str(wk+1)]
        for init in inits:
            isum = vc.Transactions.Charge().between('DATETIME', start.isoformat(), end.isoformat()).eq('INITS', init).sum('TOTAL')
            vals.append(str(isum or 0.0))
        print ",".join(vals)
        start += wkdelta
        end += wkdelta
    
    vc.close()
    
    