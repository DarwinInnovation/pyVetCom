'''
Created on 3 May 2013

@author: richardm
'''

import PyDBISAM 

class RowType(object):
    def __init__(self, val):
        self._row=val
        
    def __getattr__(self, name):
        return getattr(self._row, name)

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
            _subsets={"Invs":[("=", "TYPE", 0)], 
                      "CNs":[("=", "TYPE", 1)]
                      }
            
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
            self.__dict__[collectionName] = PyDBISAM.Collection(self, ttype, PyVetCom.Types.__dict__[type])

        # Second pass - fixup xrefs
        for typename in PyVetCom.Types.__dict__:
            if typename[0] == "_":
                continue
            ttype=getattr(PyVetCom.Types, typename)
            if hasattr(ttype, "_xrefs"):
                for t in ttype._xrefs:
                    xreftype=getattr(PyVetCom.Types, t)
                    
                    setattr(ttype, t, _getxref(xreftype._collection, ttype._xrefs[t]))
                
            

    def __init__(self):
        '''
        Constructor
        '''
        self.db = PyDBISAM.PyDBISAM()
        self.con = self.db.connect()
        self._initTables()
        
    def close(self):
        self.con.close()