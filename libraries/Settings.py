import pickle
import os.path

class SettingsList():
    def __init__(self):
        self.readSettings()
        self.settingsList['totalRunCount'] += 1
    
    def writeSettings(self):
       fileSet = open(r'settings.svset', 'wb')
       pickle.dump(self.settingsList, fileSet)
       fileSet.close() 
    
    def readSettings(self):
        try:
            file = open('settings.svset')
        except IOError as e:
            self.initDefaultSettings()
            self.writeSettings()
        else:
            with file:
                fileSet = open(r'settings.svset', 'rb')
                self.settingsList = pickle.load(fileSet)
                fileSet.close()            
        
    def printSettings(self):
        print (self.settingsList)
        
    def addSetting(self, key, value):
        self.settingsList[key] = value
        
    def initDefaultSettings(self):
        self.settingsList = {'darkColorThemeFlag' : False,
                             'darkThemeColors' : {'background' : '#303030', 
                                                  'fieldbackground' : '#303030',
                                                  'foreground' : '#bbbbbb'},
                             'totalRunCount' : 0} 
    
    def getDarkColorThemeFlag(self):
        return self.settingsList['darkColorThemeFlag']
    
    def changeDarkColorThemeFlag(self):
        self.settingsList['darkColorThemeFlag'] = not self.settingsList['darkColorThemeFlag']
        self.writeSettings()
        
    def getDarkThemeColors(self):
        return self.settingsList['darkThemeColors']
