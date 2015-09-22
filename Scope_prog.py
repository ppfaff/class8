# -*- coding: utf-8 -*-
"""
Created on Sun Sep 20 10:56:38 2015

@author: ppfaff
"""

from PyQt4 import QtGui, QtCore  # (the example applies equally well to PySide)
import pyqtgraph as pg
import channel
import sys
import os
from channel_class import SingleChannel

class Scope(QtGui.QMainWindow):
    """ Scope creates a simple data analysis window with a log of measurements
    and a oscilloscope type window to view the data.  It takes a Channel object
    to display.  It auto-adjusts the window for the data.  Window has a number
    of mouse options for changing how it displays the data
    """
    baseline = 0.0
    debug = False
    def __init__(self):
        self.sim = 0
        self.avg = 0.0
        self.Channel = SingleChannel()
        super().__init__()

        self.myinit()
        if self.Channel:
            print(self.Channel.dt)
        else:
            print("No Channel")
    
    def myinit(self):
        """ Builds the GUI window"""
        self.baseline = 0.0
        self.overlap = False
        self.time = []
        self.data = []
        self.log = []
        self.pen = 0
        self.btn = QtGui.QPushButton('Record Channel')
        self.txtlbl = QtGui.QLabel()
        self.txtlbl.setText("Cursor Value")
        self.text = QtGui.QLineEdit(str(self.baseline))
        self.spin =QtGui.QDoubleSpinBox()
        self.spin.setValue(0.0)
        self.spin.setMaximum(200)
        self.spin.setMinimum(-200)
        self.spnlbl = QtGui.QLabel()
        self.spnlbl.setText("Vm, mV")
        self.lstlbl = QtGui.QLabel()
        self.lstlbl.setText("DataLog")
        self.listw = QtGui.QListWidget()
        self.listw.setWordWrap(True)
        self.plot = pg.PlotWidget()

        # Define actions for Menu and Toolbar
        saveasAction = QtGui.QAction("&Save Log", self)
        saveasAction.setShortcut('F2')
        saveasAction.triggered.connect(self.save_log)
        exitAction = QtGui.QAction("&Quit", self)
        exitAction.setShortcut('F6')
        exitAction.triggered.connect(self.close_application)
        printAction = QtGui.QAction("&Print Log", self)
        printAction.setShortcut('F3')
        printAction.triggered.connect(self.print_log)
        measureAction = QtGui.QAction(QtGui.QIcon('ruler.png'), "&Measure", self)
        measureAction.setShortcut('F12')
        measureAction.triggered.connect(self.measure_cursor)
        zeroAction = QtGui.QAction(QtGui.QIcon('zero.png'), "&Zero Cursor", self)
        zeroAction.setShortcut('F11')
        zeroAction.triggered.connect(self.zero_cursor)
        overlapAction = QtGui.QAction(QtGui.QIcon('overlap.png'), "&Overlap Traces", self)
        overlapAction.setShortcut('F1')
        overlapAction.triggered.connect(self.toggle_overlap)
        overlapAction.setStatusTip('Toggle Trace Overlap')

        # Build the menu and toolbar
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(saveasAction)
        fileMenu.addAction(printAction)
        fileMenu.addAction(exitAction)

        self.toolbar = self.addToolBar('Measure')
        self.toolbar.addAction(measureAction)
        self.toolbar.addAction(zeroAction)
        self.toolbar.addAction(overlapAction)

        ## Create a grid layout to manage the widgets size and position
        layout = QtGui.QGridLayout()
        cent_widget = QtGui.QWidget()
        cent_widget.setLayout(layout)
        self.setCentralWidget(cent_widget)

        ## Add widgets to the layout in their proper positions
        layout.addWidget(self.btn, 0, 0)   # button goes in upper-left
        layout.addWidget(self.txtlbl, 1, 0)
        layout.addWidget(self.text, 2, 0)   # text edit goes in middle-left
        layout.addWidget(self.spnlbl, 3, 0)
        layout.addWidget(self.spin, 4, 0)   # text edit goes in middle-left
        layout.addWidget(self.lstlbl, 5, 0)
        layout.addWidget(self.listw, 6, 0)  # list widget goes in bottom-left
        layout.addWidget(self.plot, 0, 2, 7, 1)  # plot goes on right side, spanning 6 rows

        # Define event handlers
        self.btn.clicked.connect(self.buttonClicked)

        # Set up the plot window
        self.baseline = 0.0
        self.interval = 500e-3
        x_list = [0.0, self.interval]
        y_list = [self.baseline, self.baseline]
        self.plot.plot(x_list, y_list)
        self.show()

    def toggle_overlap(self):
        # Changes from Graphing single traces to overlapping traces
        if self.overlap:
            self.overlap = False
            self.plot.setTitle("")
            self.pen = 0
        else:
            self.overlap = True
            self.plot.setTitle("Overlap Traces")
            self.pen = 1
            
    def keyPressEvent(self, e):
        """ Creating simple event handlers.  Some of these will eventually be
        converted into menu items"""
        if Scope.debug: print("key", e.key(), self.baseline)
        scale = abs(self.avg)/100.0
        if e.key() == QtCore.Qt.Key_Up:
            self.baseline += scale
            self.plot.clear()
            self.plot.plot(self.time, self.data)

            self.set_baseline()
            self.text.setText(str(self.baseline))
        elif e.key() == QtCore.Qt.Key_Down:
            self.baseline -= scale
            self.plot.clear()
            self.plot.plot(self.time, self.data)
            self.set_baseline()
            self.text.setText(str(self.baseline))
        elif e.key() == QtCore.Qt.Key_PageUp:
            self.baseline += scale*10.0
            self.plot.clear()
            self.plot.plot(self.time, self.data)
            self.set_baseline()
            self.text.setText(str(self.baseline))
        elif e.key() == QtCore.Qt.Key_PageDown:
            self.baseline -= scale * 10.0
            self.plot.clear()
            self.plot.plot(self.time, self.data)
            self.set_baseline()
            self.text.setText(str(self.baseline))
        elif e.key() == QtCore.Qt.Key_F11:
            self.zero_cursor()
        elif e.key() == QtCore.Qt.Key_F12:
            self.measure_cursor()
        elif e.key() == QtCore.Qt.Key_F2:
            self.save_log()
        elif e.key() == QtCore.Qt.Key_F3:
            self.print_log()
            
    def set_baseline(self):
        """ Creates a baselie object at the indicated self.baseline point"""
        x_list = [0.0, self.interval]
        y_list = [self.baseline, self.baseline]
        self.plot.plot(x_list, y_list)
        self.text.setText(str(self.baseline))

    def buttonClicked(self):
        """ Runs a new Simulation on clicking the button"""
        self.time, self.data = self.run_channel()
        if not self.overlap:
            self.plot.clear()
        self.plot.plot(self.time, self.data, pen=self.pen)
        self.set_baseline()
        sim_ct = self.Channel.mean_ct
        sim_ot = self.Channel.mean_ot
        if Scope.debug: print("OT, CT", sim_ot, sim_ct)
        sim_str = "Simulation {0}: Vm= {1} mV, Mean Open = {2:0.4g} msec, Mean Closed = {3:0.4g} msec \n".format(
        self.sim, self.spin.text(), sim_ot * 1000.0, sim_ct * 1000.0)
        self.listw.addItem(sim_str)
        self.log.append(sim_str)
        self.sim += 1
        if self.overlap:
            self.pen += 1
        
    def measure_cursor(self):
        """ Saves the current cursor y position"""
        str_measure = "Cursor Measurement: {0:0.4g} A\n".format(self.baseline)
        self.listw.addItem(str_measure)
        self.log.append(str_measure)
    def zero_cursor(self):
        self.baseline = 0.0
        self.plot.clear()
        self.plot.plot(self.time, self.data)
        self.set_baseline()
        self.text.setText(str(self.baseline))

    def save_log(self):
        """ Simulations and cursor measures are logged.  This writes them to a file"""
        fileName = fileName = QtGui.QFileDialog.getSaveFileName(self, 'Save Data to file', '.')
        if fileName:
            print(fileName)
            with open(fileName, "w") as f:
                for element in self.log:
                    f.write(element)
                f.close()

    def print_log(self):
        """Prints the log to teh console window"""
        for element in self.log:
            print(element)

    def close_application(self):
        print("Application Exit")
        sys.exit()


    def run_channel(self):
        """ Creates single channel gating records assuming inputs are in msec units
        for all terms.  Within the program they are converted to seconds"""
        channel_data = self.Channel(float(self.spin.text())/1000.0)
        #channel_data = self.Channel.add_noise
        channel_times = [i*self.Channel.dt for i in range(len(channel_data))]
        self.avg = channel_data.mean()
        return channel_times, channel_data

def main():
    app = QtGui.QApplication(sys.argv)
    scope = Scope()
    sys.exit(app.exec_())    

if __name__ == "__main__":
    main()