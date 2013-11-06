'''
Created on 3 May 2013

@author: richardm
'''
import sys
import pyodbc
from datetime import date, time, datetime

class PyDBISAM(object):
    '''
    classdocs
    '''

    stripchars = " \t*,"

    def __init__(self, Local=0, ConnectionType="Remote", CatalogName="VetCom", IP="127.0.0.1", User="nvs", Password="rebell"):
        if Local:
            self.IP = "127.0.0.1"
        else:
            self.IP = IP

        self.ConnectionType = ConnectionType
        self.CatalogName    = CatalogName
        self.User           = User
        self.Password       = Password
        
        odbcString = "DRIVER={DBISAM 4 ODBC Driver};"
        odbcString = odbcString + "ConnectionType=" + ConnectionType + ";"
        odbcString = odbcString + "CatalogName=" + CatalogName + ";"
        odbcString = odbcString + "RemoteIPAddress=" + self.IP + ";"
        odbcString = odbcString + "UID=" + User + ";"
        odbcString = odbcString + "PWD=" + Password + ";"
        odbcString = odbcString + "ReadOnly=True;"
        self.odbcString = odbcString

    def connect(self):
        try:
            self.con = pyodbc.connect(self.odbcString)
        except:
            raise
        return self.con

    def execute(self, sql, args):
        self.con.execute(sql, args)
        
class Collection(object):
    class Query(object):
        def __init__(self, collection):
            self.collection = collection
            self.filters=[]
            self.order=[]
            
        def eq(self, column, val):
            self.filters.append(("=", column, val))
            return self
        
        def neq(self, column, val):
            self.filters.append(("<>", column, val))
            return self
        
        def gt(self, column, val):
            self.filters.append((">", column, val)) 
            return self
    
        def lt(self, column, val):
            self.filters.append(("<", column, val)) 
            return self
    
        def ge(self, column, val):
            self.filters.append((">=", column, val)) 
            return self
    
        def le(self, column, val):
            self.filters.append(("<=", column, val))
            return self
            
        def between(self, column, lo, hi): 
            self.filters.append((">=", column, lo))
            self.filters.append(("<", column, hi))
            return self
    
        def orderby(self, column):
            self.order.append(column)
            return self
            
        def getOne(self):
            return self.collection.getOne(self.filters, self.order)
        
        def getList(self):
            return self.collection.getList(self.filters, self.order)
          
        def count(self):
            return self.collection.count(self.filters, self.order)
        
        def sum(self, column):
            return self.collection.sum(self.filters, self.order, column)
    
    def _subsetClosure(self, filters):
        def method():
            q=Collection.Query(self) ;
            q.filters.extend(filters)
            return q
        return method
    
    def __init__(self, pyvc, typeName, type):
        self.pyvc = pyvc
        self.typeName=typeName
        self.type=type
        self.tableName=type._table
        type._collection=self
        self.cursor = self.pyvc.con.cursor()
        try:
            self.key=type._key
        except:
            pass
        
        try:
            for subset in type._subsets:
                setattr(self, subset, self._subsetClosure(type._subsets[subset]))
        except AttributeError:
            pass
      
    def __call__(self, keyval=None):
        if keyval is None:
            return Collection.Query(self) ;
        else:
            return self.getOne([("=",self.key,keyval)],[])
    
    def _baseSelect(self, what, filters, order):
        sql="SELECT %s FROM %s "%(what, self.tableName)
        if filters and len(filters) > 0:
            sql=sql+"WHERE "
            join=""
            for f in filters:
                cookedval=f[2]
                if type(f[2]) is str:
                    cookedval="'%s'"%(f[2])
                elif isinstance(f[2], datetime):
                        cookedval="'"+f[2].strftime("%Y-%m-%d %H:%M:%S")+"'"
                elif isinstance(f[2], date):
                        cookedval="'"+f[2].isoformat()+"'"
                
                sql=sql+join+"%s%s%s "%(f[1],f[0],cookedval)
                join="AND "
        return sql
    
    def getList(self, filters, order):
        l=[]
        sql=self._baseSelect("*", filters, order)
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        for row in rows:
            l.append(self.type(row))
        return l
        
        
    def getOne(self, filters, order):
        sql=self._baseSelect("*", filters, order)+"TOP 1 "
        self.cursor.execute(sql)
        
        row=self.cursor.fetchone()
        if row is not None:
            return self.type(row)
        else:
            return None
    
    def count(self, filters, order):
        sql=self._baseSelect("COUNT(*)", filters, order)+"TOP 1 "
        self.cursor.execute(sql)
        
        row=self.cursor.fetchone()
        if row is not None:
            return row[0]
        else:
            return 0
    
    def sum(self, filters, order, column):
        sql=self._baseSelect("SUM(%s)"%column, filters, order)+"TOP 1 "
        self.cursor.execute(sql)
        
        row=self.cursor.fetchone()
        if row is not None:
            return row[0]
        else:
            return 0
    
    