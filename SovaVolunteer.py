versionPR = "SovaVolunteer 0.9(beta)"
versionDate = "24.01.19"
changeList = [(1, "убрана строгая проверка ников"),
              (2, "добавлено модальное окно при \n совпадении ников")]
updateLink = "https://drive.google.com/file/d/1uGX9LUnL_CMMwcHQt6xYuzchfIu0yrde/view"

from tkinter import tix as tk

import sqlite3
from tkinter import *
from tkinter import ttk
import logging
import webbrowser
import time

# add filemode="w" to overwrite

logging.basicConfig(filename="sova.log", level=logging.INFO, format = "%(asctime)s %(levelname)s - %(message)s") 

#logging.debug("")
#logging.info("")
#logging.error("")

def stopLogging():
    logging.shutdown()

class Volunteer():
    def __init__(self, strinFromDB):
      self.id = strinFromDB[0]  
      self.name = strinFromDB[1]
      self.nick = strinFromDB[2]
      self.info = strinFromDB[3]
      self.departament = strinFromDB[4]
    
    def getId(self):
        return self.id       
    def getName(self):
        return self.name
    def getNick(self):
        return self.nick
    def getInfo(self):
        return self.info
    def getDepartament(self):
        return self.departament       

def errorFrame(errorText):
    errorF = Toplevel()
    errorF.title("Error")
    errorF.geometry("300x100")
    def closeThisErrorFrame():
       errorF.destroy() 
    labelVersionData = Label(errorF,
                             text=("Ваши последние действия привели\n к возникновению ошибки: \n" + errorText))
    labelVersionData.pack(fill=BOTH, padx=5, pady=5)
    button_accept = Button(errorF, text = 'Ok', command = closeThisErrorFrame)
    button_accept.pack(padx=5, pady=5)
    

class datBaseConnector():
    def __init__(self): 
        logging.info("init connection")
        self.conn = sqlite3.connect('SovaVolunteeres.sqlite', timeout=100)
        self.cursor = self.conn.cursor()
        self.creator()      
    
    def execute(self, query, param = None):
        logging.info(query + " " + (str(param)))
        try:
            if param == None:
                self.cursor.execute(query)
            else:
                self.cursor.execute(query, param)
                self.conn.commit()
        except Exception as err:
            logging.error('execute failed: %s : %s' % (query, str(err)))
            errorFrame(str(err))
        cursorT = self.cursor
        return cursorT
        
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
        
    def selectAllVolunteeres(self): 
        stringToExec = "select full_Name from human_resources"
        return self.stringArrConstructor(self.execute(stringToExec))
    
    def insertNewVolunteer(self, insertData):
        stringToExec = "insert into human_resources values(NULL,?,?,?,?)"
        self.execute(stringToExec, insertData)
        
    def isertNick(self, nick):
        stringToExec = "insert into empty_callsign values(NULL, '" + nick + "')"
        self.execute(stringToExec)
            
    def emptyNick(self, checkNick):
        stringToExec = "select * from empty_callsign where callsign = '" + checkNick + "'"
        return self.execute(stringToExec).fetchone()
    
    def deleteNick(self, nick):
        stringToExec = "delete from empty_callsign where callsign = '" + nick + "'"
        self.execute(stringToExec)
    
    def selectAllUniqDepartaments(self):
        stringToExec = "select distinct departament from human_resources"
        return self.stringArrConstructor(self.execute(stringToExec))
    
    def selectByName(self, userName): 
        stringToExec = "select full_name, callsign, additional_information from human_resources where full_name = '" + userName + "'"
        return self.stringArrConstructor(self.execute(stringToExec))
    
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
        print(stringToExec)
        temp = self.execute(stringToExec).fetchone()
        print(temp)
        print(temp != None)
        return temp != None
    
    def existNickInPeopleTable(self, sovaVolontCall):
        stringToExec = "select * from human_resources where upper(callsign) = upper('"
        stringToExec +=  sovaVolontCall + "') limit 1"
        temp = self.execute(stringToExec).fetchone()
        return temp != None
    
    def selectVolunteerById(self, idDB):
        stringToExec = "select * from human_resources where id = " + str(idDB)
        getStr = str(self.execute(stringToExec).fetchone())
        getStr = getStr.replace("(", "")
        getStr = getStr.replace(")", "")
        getStr = getStr.replace("'", "")
        arr = getStr.split(', ')
        return Volunteer(arr)
    
    def selectByDepartament(self, departament): 
        stringToExec = "select * from human_resources where departament = '" + departament + "'"
        return self.execute(stringToExec).fetchall()
    
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
    
class GeneralFrame(Frame):
    value = 1
    def __init__(self, parent):
        Frame.__init__(self, parent)   
        self.parent = parent
        self.dbSova = datBaseConnector()
        self.initUI()

    def initUI(self):
        self.dbSova.creator()
        self.parent.title("SovaVolunteer")          
        self.pack(fill=BOTH, expand=1)
        self.var = []   
        self.id = None
        
        self.configTreeView()
        
        frame = Frame(self)
        frame.pack()
        button_accept = Button(frame, text = 'Добавить волонтера', command = self.createNewVolunteer)
        button_accept.pack(side = LEFT, padx=5, pady=5) 
        button_help = Button(frame, text = '?', command = self.showAbout)
        button_help.pack(side = RIGHT, padx=5, pady=5) 
    
    def showAbout(self):
        top = Toplevel()
        top.title("About SovaVolunteer")
        top.geometry("300x240")
        labelVersion = Label(top, text=("Версия сборки: " + versionPR))
        labelVersion.pack(padx=5, pady=5)
        labelProgrammist = Label(top, text=("Efremov Dmitry© " + versionDate))
        labelProgrammist.pack(side=BOTTOM, padx=5, pady=5)
        def downloadNew():
            webbrowser.open_new(updateLink)
        button_accept = Button(top, text = 'Скачать новую версию', command = downloadNew)
        button_accept.pack(side=BOTTOM, padx=25, pady=5) 
        versionChangeStr = ""
        for changeEl in changeList:
            versionChangeStr += str(changeEl[0]) + ". " + changeEl[1] + "\n" 
        labelVersionData = Label(top, text=(versionChangeStr))
        labelVersionData.pack(padx=5, pady=5)
        
    
    def funcDelete(self):
        top = Toplevel()
        top.title("Удаление волонтера")
        top.geometry("500x80")
        labelTableName = Label(top, text=("Действительно удалить волонтера " + str(self.var[0]) + "?"))
        labelTableName.pack(side=TOP, padx=5, pady=5) 
        x = (root.winfo_reqwidth()) / 2
        y = (root.winfo_reqheight()) / 2
        top.wm_geometry("+%d+%d" % (x, y))     
        def deletefromTable():
            self.dbSova.isertNick(self.dbSova.selectVolunteerById(self.id).getNick())
            self.dbSova.deletFromVolunteeres(self.id)
            self.updateTreeView()
            top.destroy()
        def cancel():
            top.destroy()
        button_decine = Button(top, text = 'Отменить удаление', command = cancel)
        button_decine.pack(side=RIGHT, padx=90, pady=5)
        button_accept = Button(top, text = 'Подтвердить', command = deletefromTable)
        button_accept.pack(side=RIGHT, padx=25, pady=5)
        top.grab_set()
        top.focus_set()
        top.wait_window()
        
    def acceptOrRejectModal(self, textAlert, acceptF, rejectF):
        acceptOrReject = Toplevel()
        acceptOrReject.title("Подтверждение действия")
        widthFrame = 400
        if(len(textAlert) * 8 > widthFrame):
            widthFrame = len(textAlert) * 8
        acceptOrReject.geometry(str(widthFrame) + "x80")
        labelTableName = Label(acceptOrReject, text=textAlert)
        labelTableName.grid(row = 0, column = 0, columnspan = 3, padx=5, pady=5) 
        def accept():
            acceptF()
            acceptOrReject.destroy()
        def reject():
            acceptOrReject.destroy()
            rejectF()
        button_decine = Button(acceptOrReject, text = 'Отменить', command = reject)
        button_decine.grid(row = 1, column = 1, padx=5, pady=5) 
        button_accept = Button(acceptOrReject, text = 'Подтвердить', command = accept)
        button_accept.grid(row = 1, column = 2, padx=5, pady=5) 
        
    def createNewVolunteer(self):
        top = Toplevel()
        top.title("Создание волонтера")
        top.geometry("600x310")
        x = (root.winfo_reqwidth()) / 2
        y = (root.winfo_reqheight()) / 2
        top.wm_geometry("+%d+%d" % (x, y))     
        def createNew():
            def insertNew():
                self.dbSova.insertNewVolunteer([nameField.get('1.0', END)[:-1],
                                                    nickField.get('1.0', END)[:-1],
                                                    infoField.get('1.0', END)[:-1],
                                                    depField.get('1.0', END)[:-1]])
                self.dbSova.deleteNick(nickField.get('1.0', END)[:-1])
                self.updateTreeView()
                top.destroy()
            def tryAgain():
                return
            if(self.dbSova.existNickInPeopleTable(nickField.get('1.0', END)[:-1])):
                self.acceptOrRejectModal("Введеный позывной уже используется, все равно добавить?", insertNew, tryAgain)
            else:
                if (nameField.get('1.0', END)[:-1] != ''):
                    insertNew()
        def cancel():
            top.destroy()
        
        def checkNick():
            checker = Toplevel(top)
            checker.title("Проверка ника")
            checker.geometry("400x80")
            checkInCall = "Проверка на корректность позывного - "
            checkInHumans = "Проверка на возможность назначения позывного - "
            if(self.dbSova.existNickInNickTable(nickField.get('1.0', END)[:-1])):
                checkInCall += "пройдено"
            else:
                checkInCall += "НЕ пройдено"
            if(self.dbSova.existNickInPeopleTable(nickField.get('1.0', END)[:-1])):
                checkInHumans += "НЕ пройдено"
            else:
                checkInHumans += "пройдено"
            labelFCheck = Label(checker, text = checkInCall).pack()
            labelSCheck = Label(checker, text = checkInHumans).pack()
            
        
        labelName = Label(top, text = 'ФИО:').grid(row = 0, padx=5, pady=5)
        nameField = Text(top, height=1, width=50, font='Arial 10', wrap = WORD)
        nameField.grid(row = 0, column = 1, columnspan = 3,  padx=5, pady=5)

        labelNick = Label(top, text = 'Позывной:').grid(row = 1, padx=5, pady=5)
        nickField = Text(top, height=1, width=35, font='Arial 10', wrap = WORD)
        nickField.grid(row = 1, column = 1, columnspan = 2,  padx=5, pady=5)
        
        button_decine = Button(top, text = 'Проверить ник', command = checkNick)
        button_decine.grid(row = 1, column = 3, padx=5, pady=5)
        
        labelInfo = Label(top, text = 'Дополнительная информация:').grid(row = 3, padx=5, pady=5)
        infoField = Text(top, height=10, width=50, font='Arial 10', wrap = WORD)
        infoField.grid(row = 2, column = 1, rowspan=3, columnspan = 3, padx=5, pady=5)
                
        labelDep = Label(top, text = 'Подразделение:').grid(row = 5, padx=5, pady=5)
        depField = Text(top, height=1, width=50, font='Arial 10', wrap = WORD)
        depField.grid(row = 5, column = 1, columnspan = 3,  padx=5, pady=5)

        button_decine = Button(top, text = 'Отмена', command = cancel)
        button_decine.grid(row = 6, column = 2, padx=5, pady=5)
        button_accept = Button(top, text = 'Создать', command = createNew)
        button_accept.grid(row = 6, column = 1, padx=5, pady=5)
#        top.grab_set()
#        top.focus_set()
#        top.wait_window()
    
    def configTreeView(self):
        self.tree = ttk.Treeview(self)
        self.tree["columns"]=("name","nick", "info")
        self.tree.column("name", width=100 )
        self.tree.column("nick", width=100)
        self.tree.column("info", width=100 )
        self.tree.heading("name", text="ФИО")
        self.tree.heading("nick", text="Позывной")
        self.tree.heading("info", text="Дополнительная информция")
        self.tree.pack(expand=True, fill='both', padx = 5, pady = 5)
        self.tree.bind('<<TreeviewSelect>>', self.onSelect) 
        self.tree.bind("<Double-1>", self.OnDoubleClick)
        self.updateTreeView()
    
    def updateTreeView(self):
        self.tree.delete(*self.tree.get_children())
        j = 0
        departaments = self.dbSova.selectAllUniqDepartaments()
        for departament in departaments:
            volonts= []
            humans = self.dbSova.selectByDepartament(departament)
            for human in humans:
                volonts.append(Volunteer(human))
            id2 = self.tree.insert("", 1, "depart" + str(j), text=departament)
            i = 0
            for volont in volonts:
                 self.tree.insert(id2, "end", str(volont.getId()), text=departament, tags = str(volont.getId()), values=(volont.getName(),volont.getNick(), volont.getInfo()))
                 i += 1
            j += 1

    def updateVolunteer(self):
        top = Toplevel()
        top.title("Изменение данных волонтера")
        top.geometry("600x310")
        
        sovaVolunteer = self.dbSova.selectVolunteerById(self.id)
        
        labelName = Label(top, text = 'ФИО:').grid(row = 0, padx=5, pady=5)
        nameField = Text(top, height=1, width=50, font='Arial 10', wrap = WORD)
        nameField.insert(1.0, str(sovaVolunteer.getName()))
        nameField.grid(row = 0, column = 1, columnspan = 3,  padx=5, pady=5)

        labelNick = Label(top, text = 'Позывной:').grid(row = 1, padx=5, pady=5)
        nickField = Text(top, height=1, width=50, font='Arial 10', wrap = WORD)
        nickField.insert(1.0, str(sovaVolunteer.getNick()))
        nickField.grid(row = 1, column = 1, columnspan = 3,  padx=5, pady=5)
        
        labelInfo = Label(top, text = 'Дополнительная информация:').grid(row = 3, padx=5, pady=5)
        infoField = Text(top, height=10, width=50, font='Arial 10', wrap = WORD)
        infoField.insert(1.0, str(sovaVolunteer.getInfo()))
        infoField.grid(row = 2, column = 1, rowspan=3, columnspan = 3, padx=5, pady=5)
                
        labelDep = Label(top, text = 'Подразделение:').grid(row = 5, padx=5, pady=5)
        depField = Text(top, height=1, width=50, font='Arial 10', wrap = WORD)
        depField.insert(1.0, str(sovaVolunteer.getDepartament()))
        depField.grid(row = 5, column = 1, columnspan = 3,  padx=5, pady=5)
        
        def updateSova():
            sovaVolunteer.name = nameField.get('1.0', END)[:-1]
            sovaVolunteer.nick = nickField.get('1.0', END)[:-1]
            sovaVolunteer.info = infoField.get('1.0', END)[:-1]
            sovaVolunteer.departament = depField.get('1.0', END)[:-1]
            self.dbSova.updateVolunteer(sovaVolunteer)
            self.updateTreeView()
            top.destroy()
        def cancel():
            top.destroy()
        button_decine = Button(top, text = 'Удалить волонтера', command = self.funcDelete)
        button_decine.grid(row = 6, column = 2, padx=5, pady=5)
        button_accept = Button(top, text = 'Сохранить', command = updateSova)
        button_accept.grid(row = 6, column = 1, padx=5, pady=5)
        
    def OnDoubleClick(self, event):
        sender = event.widget
        curItem = sender.focus()
        if(sender.item(curItem)['values']):
            self.id = sender.item(curItem)['tags'][0]
            self.updateVolunteer()
    
    def onSelect(self, val):
        sender = val.widget
        curItem = sender.focus()
        if(sender.item(curItem)['values']):
            self.var = (sender.item(curItem)['values'])
            self.id = sender.item(curItem)['tags'][0]

root=Tk()
var = StringVar()
root.geometry("800x500")
GeneralFrame(root)    
root.mainloop()