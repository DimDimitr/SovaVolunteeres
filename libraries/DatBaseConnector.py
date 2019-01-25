import logging
import sqlite3

# add filemode="w" to overwrite

logging.basicConfig(filename="sova.log", level=logging.INFO, format = "%(asctime)s %(levelname)s - %(message)s") 

#logging.debug("")
#logging.info("")
#logging.error("")

def stopLogging():
    logging.shutdown()

class datBaseConnector():
    def __init__(self): 
        logging.info("init connection")
        self.conn = sqlite3.connect('SovaVolunteeres.sqlite', timeout=100)
        self.cursor = self.conn.cursor()
        self.creator()      
    
    #returnMode:
    #fetchOne
    #fetchAll
    #strCostr
    def execute(self, query, param = None, returnMode = ''):
        logging.info(query + " " + (str(param)))
        self.conn = sqlite3.connect('SovaVolunteeres.sqlite', timeout=100)
        self.cursor = self.conn.cursor()
        try:
            if param == None:
                self.cursor.execute(query)
            else:
                self.cursor.execute(query, param)
            self.conn.commit()
        except Exception as err:
            logging.error('execute failed: %s : %s' % (query, str(err)))
            errorFrame(str(err))
        result = None
        if(returnMode == 'fetchOne'):
            result = self.cursor.fetchone()
        elif(returnMode == 'fetchAll'):
            result = self.cursor.fetchall()
        elif(returnMode == 'strCostr'):
            result = self.stringArrConstructor(self.cursor)
        self.closeConnect()
        return result
        
    def creator(self):
        self.execute("""create table if not exists human_resources
                   (id integer primary key autoincrement,
                   full_name text not null,
                   callsign text,
                   additional_information text,
                   departament text,
                   CONSTRAINT constraint_name UNIQUE(callsign))""") 
        self.execute("""create table if not exists empty_callsign
                   (id integer primary key autoincrement,
                   callsign text not null
                   )""")
        
    def createTestData(self):
        self.execute("delete from human_resources")
        #имя, позывной, инфо, отряд
        departaments = ['Тверь', 'Ржев', 'Кимры', 'Конаково']
        for dapart in departaments:
            i = 0
            while i < 10:
                self.insertNewVolunteer(['Имя' + dapart + str(i), dapart + str(i), 'info ' + str(i), dapart])
                i += 1
        
    def selectAllVolunteeres(self): 
        stringToExec = "select full_Name from human_resources"
        return self.execute(stringToExec, returnMode = 'strCostr')
    
    def insertNewVolunteer(self, insertData):
        stringToExec = "insert into human_resources values(NULL,?,?,?,?)"
        self.execute(stringToExec, insertData)
        
    def isertNick(self, nick):
        stringToExec = "insert into empty_callsign values(NULL, '" + nick + "')"
        self.execute(stringToExec)
            
    def emptyNick(self, checkNickState):
        stringToExec = "select * from empty_callsign where callsign = '" + checkNickState + "'"
        return self.execute(stringToExec, returnMode = 'fetchOne')
    
    def deleteNick(self, nick):
        stringToExec = "delete from empty_callsign where callsign = '" + nick + "'"
        self.execute(stringToExec)
    
    def selectAllUniqDepartaments(self):
        stringToExec = "select distinct departament from human_resources"
        return self.execute(stringToExec, returnMode = 'strCostr')
    
    def selectByName(self, userName): 
        stringToExec = "select full_name, callsign, additional_information from human_resources where full_name = '" + userName + "'"
        return self.execute(stringToExec,  returnMode = 'strCostr')
    
    def updateVolunteer(self, sovaVolont):
        stringToExec = "update human_resources set full_name = '"  + sovaVolont.getName() + "', "
        stringToExec += "callsign = '"  + sovaVolont.getNick() + "', "
        stringToExec += "additional_information = '"  + sovaVolont.getInfo() + "', "
        stringToExec += "departament = '"  + sovaVolont.getDepartament() + "' "
        stringToExec += "where id = " + sovaVolont.getId()
        self.execute(stringToExec)
    
    def existNickInNickTable(self, sovaVolontCall):
        stringToExec = "select * from empty_callsign where upper(callsign) = upper('"
        stringToExec +=  sovaVolontCall + "') limit 1"
        return self.execute(stringToExec, returnMode = 'fetchOne') != None
    
    def existNickInPeopleTable(self, sovaVolontCall):
        stringToExec = "select * from human_resources where upper(callsign) = upper('"
        stringToExec +=  sovaVolontCall + "') limit 1"
        return self.execute(stringToExec, returnMode = 'fetchOne') != None
    
    def selectVolunteerById(self, idDB):
        stringToExec = "select * from human_resources where id = " + str(idDB)
        getStr = str(self.execute(stringToExec, returnMode = 'fetchOne'))
        getStr = getStr.replace("(", "")
        getStr = getStr.replace(")", "")
        getStr = getStr.replace("'", "")
        arr = getStr.split(', ')
        return Volunteer(arr)
    
    def selectByDepartament(self, departament): 
        stringToExec = "select * from human_resources where departament = '" + departament + "' order by full_name asc"
        return self.execute(stringToExec, returnMode = 'fetchAll')
    
    def deletFromVolunteeres(self, id):
        stringToExec = "delete from human_resources where id = " + str(id)
        self.execute(stringToExec)
    
    def stringArrConstructor(self, cursor):
        endStr = []
        firstDat = cursor.fetchone()
        while firstDat is not None:
            firstDat = str(firstDat)
            firstDat = firstDat[2:-3]
            endStr.append(str(firstDat))
            firstDat = cursor.fetchone()
        return endStr
    
    def closeConnect(self):
        logging.info("closeConnect")
        self.conn.close()