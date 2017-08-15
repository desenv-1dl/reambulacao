# -*- coding: utf-8 -*-
from PyQt4.QtCore import Qt, SIGNAL
from PyQt4.QtGui import QShortcut, QKeySequence
class ShortCut:
    def __init__(self, local, tabs, buttons):
        self.local = local
        self.mapShortcuts = None
        self.setButtons(buttons)
        self.tab = tabs
        self.initShorts()
    
    def initShorts(self):
        teste = {
                 Qt.Key_0 : 0, 
                 Qt.Key_1 : 1,
                 Qt.Key_2 : 2,
                 Qt.Key_3 : 3,
                 Qt.Key_4 : 4,
                 Qt.Key_5 : 5,
                 Qt.Key_6 : 6,
                 Qt.Key_7 : 7,
                 Qt.Key_8 : 8,
                 Qt.Key_9 : 9
                 }
        
        teste2 = {
                  Qt.Key_F3 : u'select',          
                  Qt.Key_F4 : u'form'
                  }
        for k in teste:
           self.local.connect(QShortcut(QKeySequence(k), self.local), SIGNAL('activated()'), lambda value=teste[k]: self.clic(value))
        for b in teste2:
           self.local.connect(QShortcut(QKeySequence(b), self.local), SIGNAL('activated()'), lambda value=teste2[b]: self.clic2(value)) 
    
    def clic(self, key):
        if self.getMapShortcuts():
            categoria = self.tab.currentWidget().objectName()
            if not(self.getMapShortcuts()[categoria] == {}) and (key in self.getMapShortcuts()[categoria]):
                self.getMapShortcuts()[categoria][key].click()
                
    def clic2(self, key):
        if self.getButtons():
            self.getButtons()[key].click()
                   
    def setMapShortcuts(self, m):
        self.mapShortcuts = m 
        
    def getMapShortcuts(self):
        return self.mapShortcuts
    
    def setButtons(self, m):
        self.buttons = m 
        
    def getButtons(self):
        return self.buttons
    
    
