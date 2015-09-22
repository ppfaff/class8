# -*- coding: utf-8 -*-
"""
Created on Sun Sep 20 19:13:04 2015

@author: ppfaff
"""
from Scope_prog import Scope
from PyQt4 import QtGui
import sys

app = QtGui.QApplication(sys.argv)
scope = Scope()
sys.exit(app.exec_())    
