'''
Created on 3 May 2013

@author: richardm
'''

import PyDBISAM 
import datetime

class RowType(object):
    def __init__(self, val):
        self._row=val
        
    def __getattr__(self, name):
        return getattr(self._row, name)
    
    def dict(self):
        d={}
        for i in range(len(self._row.cursor_description)):
            c = self._row.cursor_description[i]
            v = self._row[i]
            
            # Fix types
            if hasattr(v, 'isoformat'):
                v=v.isoformat()
            elif isinstance(v, basestring):
                v=unicode(v, 'iso-8859-1')

            d[c[0]] = v
        return d

def _getxref(xrefcollection, column):
    def get(self):
        return xrefcollection(getattr(self, column))
    
    return get

class PyVetCom(object):
    '''
    classdocs
    '''
    
    class Types:
        class Client(RowType):
            _table="CL"
            _key="CLNO"
            _datetime="ACCESS"
            
        class Animal(RowType):
            _table="AN"
            _key="ANNO"
            _xrefs={"Client":"CLNO"}
            
        class Appt(RowType):
            _table="WL"
            _xrefs={"Client":"CLNO", "Animal":"ANNO"}
            
        class SLDoc(RowType):
            _table="SL"
            _xrefs={"Client":"CLNO"}
            _subsets= dict(
                Invs=[("=", "TYPE", 0)],
                CNs=[("=", "TYPE", 1)],
                PaymentCash=[("=", "TYPE", 2)],
                PaymentChq=[("=", "TYPE", 3)],
                PaymentCC=[("=", "TYPE", 4)],
                PaymentTrf=[("=", "TYPE", 5)],
                JournalDebit=[("=", "TYPE", 6)],
                JournalCredit=[("=", "TYPE", 7)],
                Payments=[(">=", "TYPE", 2), ("<=", "TYPE", 5)])
            
        class Transaction(RowType):
            _table="TR"
            _xrefs={"Client":"CLNO", "Animal":"ANNO", "SLDoc":"DOCNO"}
            _subsets={"Charge":[("=", "TYPE", 'I')], 
                      "Credit":[("=", "TYPE", 'C')],
                      "Receipt":[("=", "TYPE", 'R')]
            }
            
        class Note(RowType):
            _table="CN"
            _xrefs={"Animal":"ANNO"}
            _subsets={"Disp":[("=", "TYPE", 'D')], 
                      "Vet":[("=", "TYPE", 'C')],
                      "Inv":[("=", "TYPE", 'I')],
                      "Lab":[("=", "TYPE", 'L')]
                      }
   
    def _initTables(self):
        for ttype in PyVetCom.Types.__dict__:
            if ttype[0] == "_":
                continue
            
            collectionName = ttype + "s"
            self.__dict__[collectionName] = PyDBISAM.Collection(self, ttype, PyVetCom.Types.__dict__[ttype])

        # Second pass - fixup xrefs
        for typename in PyVetCom.Types.__dict__:
            if typename[0] == "_":
                continue
            ttype=getattr(PyVetCom.Types, typename)
            if hasattr(ttype, "_xrefs"):
                for t in ttype._xrefs:
                    xreftype=getattr(PyVetCom.Types, t)
                    
                    setattr(ttype, t, _getxref(xreftype._collection, ttype._xrefs[t]))
                
            

    def __init__(self, ip):
        '''
        Constructor
        '''
        if ip is None:
            ip="127.0.0.1"

        self.db = PyDBISAM.PyDBISAM(IP=ip)
        self.con = self.db.connect()
        self._cursor = None
        
        self._initTables()
        
    def execute(self, sql, args=None):
        self.db.execute(sql, args)
        
    def convDate(self, dt):
        if isinstance(dt, datetime.datetime):
            dt = dt.date()
            
        return dt.strftime('%Y-%m-%d') 

    def cursor(self):
        if self._cursor is None:
            self._cursor = self.con.cursor()
        return self._cursor

    def close(self):
        self.con.close()
        pass
