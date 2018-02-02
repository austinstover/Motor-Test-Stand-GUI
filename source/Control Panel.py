#!/usr/bin/python
# -*- coding: utf-8 -*-

# Christophe Foyer & Austin Stover 2017

#TODO: 1. Fix scaling

### DEPENDENCIES ###
# - Tkinter        #
# - pySerial       #
# - MatPlotLib     #
# - numpy          #
####################

import Tkinter as tk
from Tkinter import Tk, BOTH, OptionMenu, IntVar, LEFT, Canvas, Frame, W, X, N, Y, BooleanVar, StringVar
from ttk import Frame, Button, Style, Label, Scale, Checkbutton, Entry
import tkMessageBox as messagebox

import serial
import csv

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure

from threading import Thread
from multiprocessing import Queue

import time
import sys
import glob

#import Austin's script
from SerialComm.SerialComm import SerialComm
from collections import deque

def main():

    print "Initializing"
    print "Displaying GUI"

    root = Tk()
    app = mSim(root)
    root.resizable(0,0) #This removes the maximize button (was causing issues with scaling, not ideal)
    root.iconbitmap('favicon.ico') #favicon (so pretty)

    #Define closing behavior
    def on_closing():
        if messagebox.askokcancel("Quit", "Do you want to quit?"): #textbox on exit
            root.destroy()

    #set closing behavior
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    #start GUI
    root.mainloop()

class mSim(Frame):
  
    def __init__(self, parent):
        
        self.serialStatus = False

        #create variables
        self.startmotor = BooleanVar()
        self.logstate = BooleanVar()
        self.throttlevar = StringVar()
        self.throttleval = IntVar()

        #default values
        self.throttlevar.set("0%")
        self.throttleval.set(0)

        #base frame init
        Frame.__init__(self, parent)   
        self.parent = parent
        self.initUI()
        self.centerWindow()

        self.PERIOD_LENGTH_Log = 100 #milliseconds
        self.PERIOD_LENGTH_Scan = 1000 #milliseconds
        self.PERIOD_LENGTH_Refresh = 300 #milliseconds

        self.parent.after(0, self.runScan)
        self.parent.after(0, self.runLog)
        self.parent.after(0, self.runRefresh)
        

    def runScan(self):
        #serial port scanning function
        """ Lists serial port names

            :raises EnvironmentError:
                On unsupported or unknown platforms
            :returns:
                A list of the serial ports available on the system
        """
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        menu = self.drop["menu"]
        menu.delete(0, "end")
        menu.add_command(label="None", command=lambda value="None": self.selected_s_Port.set(value))
        for string in result:
            menu.add_command(label=string, command=lambda value=string: self.selected_s_Port.set(value))
                
        self.parent.after(self.PERIOD_LENGTH_Scan, self.runScan)

    def runLog(self):
        if (self.logstate.get() == True) and (self.serialStatus == True): #logging data                                        
                    data = dict(zip(*[self.SC.dict.keys(), zip(*self.SC.dict.values())[-1]])) 
                    if 'l' not in locals():         # a dictionary with a deque of the recent data for each message type -Austin
                        l = []
                    if self.loggedData == []: #if empty add titles
                        l=[data.keys()]
                    data = data.values()
                    l.append(data)
                    self.loggedData = l #this is an array (that way I don't have to change my csv code)
                    
        self.parent.after(self.PERIOD_LENGTH_Log, self.runLog)

    def runRefresh(self):
        
        #Refresh figures function
        self.a.clear()
        self.b.clear()
        self.c.clear()
        self.d.clear()
        
        if not self.serialStatus:
            #TODO: Put SerialComm data buffer here v . Timestamps (from python?) on x axis, values on y-axis
            #Helpful Info: plot([xvals],[yvals])
            self.a.plot([0],[0])
            self.b.plot([0],[0])
            self.c.plot([0],[0])
            self.d.plot([0],[0])
        else:
            self.SC.processData(5) # This param is the number of bytes to try for a message -Austin
            timestamps = [val / 1000.0  if val != None else val for val in self.SC.dict['Timestamp']]
            self.a.plot(timestamps, self.SC.dict['Thrust'])
            self.b.plot(timestamps, self.SC.dict['Rot Speed'])
            self.c.plot(timestamps, self.SC.dict['Current'])
            self.d.plot(timestamps, self.SC.dict['Voltage'])

        #set labels for graphs (could make automatic later)
        self.a.set_xlabel('time (s)')
        self.a.set_ylabel('Thrust (N)')
        self.b.set_xlabel('time (s)')
        self.b.set_ylabel('RPM')
        self.c.set_xlabel('time (s)')
        self.c.set_ylabel('Current (A)')
        self.d.set_xlabel('time (s)')
        self.d.set_ylabel('Voltage (V)')

        #try drawing the canvas
        try:
            self.canvas.draw()
        except:
            pass #just ignore it, you'll do better next time
        
        self.parent.after(self.PERIOD_LENGTH_Refresh, self.runRefresh)

    def centerWindow(self):
      
        w = 800 #eh, who needs scaling anyways
        h = 500

        sw = self.parent.winfo_screenwidth()
        sh = self.parent.winfo_screenheight()
        
        x = (sw - w)/2
        y = (sh - h)/2
        self.parent.geometry('%dx%d+%d+%d' % (w, h, x, y))
        

    def initUI(self):

        #Parent Frame
        self.parent.title("Test Stand Control Panel")
        self.style = Style()
        self.style.theme_use("default")

        self.pack(fill=BOTH, expand=1)


        # Frame 1 (top)
        frame1 = Frame(self)
        frame1.pack(fill=X, expand=1)

            #Start motor button
        startButton = Button(frame1, text="Start Motor",
            command=self.startMotor)
        startButton.pack(side=LEFT, padx=5, pady=5)     


            #Throttle slider
        lbl1 = Label(frame1, text="Throttle (0-100):", width=14)
        lbl1.pack(side=LEFT, padx=5, pady=5)
        
        self.scale = Scale(frame1, from_=0, to=100, 
            command=self.onScaleThrottle)
        self.scale.pack(side=LEFT, padx=15)
        
        self.label = Label(frame1, text="throttle", textvariable=self.throttlevar, width=5)        
        self.label.pack(side=LEFT)

            #Throttlesweep checkbutton
        self.autovar = BooleanVar()
        cb = Checkbutton(frame1, text="Throttle Sweep",
            variable=self.autovar, command=self.onClickAuto)
        cb.pack(side=LEFT, padx=15)

            #Com port selection field
        droplbl = Label(frame1, text="Serial Port:", width=10)
        droplbl.pack(side=LEFT, padx=5, pady=5)
        self.selected_s_Port = StringVar()
        self.s_Ports = []
        self.drop = OptionMenu(frame1,self.selected_s_Port,"None",*self.s_Ports)
        self.drop.pack(side=LEFT, padx=5)

            #baudrate selection field (disabled)
##       drop2lbl = Label(frame1, text="Baudrate:", width=9)
##        drop2lbl.pack(side=LEFT, padx=5, pady=5)
##        self.baudrate = StringVar()
##        baudrates = [9600, 19200, 38400, 57600, 115200]
##        drop2 = OptionMenu(frame1,self.baudrate,*baudrates)
##        drop2.pack(side=LEFT, padx=5)

            #Start serial button
        comsButton = Button(frame1, text="Start Serial",
            command=self.startSerial)
        comsButton.pack(side=LEFT, padx=5, pady=5)

            #Stop serial button
        comsStopButton = Button(frame1, text="Stop Serial",
            command=self.stopSerial)
        comsStopButton.pack(side=LEFT, padx=5, pady=5)

        # Frame 2 (second line)
        frame2 = Frame(self)
        frame2.pack(fill=X, expand=1)

            #Amperage entry
        lbl2 = Label(frame2, text="Max Motor Current (A):", width=21)
        lbl2.pack(side=LEFT, padx=5, pady=5)
        
        self.MaxA_Entry = Entry(frame2)
        self.MaxA_Entry.pack(side="left", fill=X, padx=5, expand=False)
        self.MaxA_Entry.insert(0, 10)

            #Voltage entry
        lbl3 = Label(frame2, text="Max Motor Voltage (V):", width=20)
        lbl3.pack(side=LEFT, padx=5, pady=5)
        
        self.MaxV_Entry = Entry(frame2)
        self.MaxV_Entry.pack(side="left", fill=X, padx=5, expand=False)
        self.MaxV_Entry.insert(0, 14)

            #Update button
        updateButton = Button(frame2, text="Update Values",
            command=self.updateValues)
        updateButton.pack(side=LEFT, padx=5, pady=5)
        
        # Graph Frame
        framegraph = Frame(self)
        framegraph.pack(fill=X, expand=1)

            #Init figures
        f = Figure(figsize=(4,4), dpi=100)
        self.a = f.add_subplot(2, 2, 1)
        self.d = f.add_subplot(2, 2, 4)
        self.c = f.add_subplot(2, 2, 3)
        self.b = f.add_subplot(2, 2, 2)
        
        f.set_tight_layout(True)

        self.canvas = matplotlib.backends.backend_tkagg.FigureCanvasTkAgg(f, master=self)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

            #Display Toolbar
        toolbar = NavigationToolbar2TkAgg(self.canvas, framegraph)
        toolbar.update()
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Frame 0 (Bottom text)
        frame0 = Frame(self)
        frame0.pack(side="bottom", fill="x", expand=1)

            #Display text (allows to give user information)
        self.textboxvar = StringVar()
        self.info = Label(frame0, textvariable=self.textboxvar)
        self.info.pack(side=LEFT, padx=5, pady=5)

        # Button Frame (large buttons, near bottom)
        s = Style() #has its own style
        s.configure('My.TFrame',background='#f7edc3') #fancy colors
        framered = Frame(self, style='My.TFrame')
        framered.pack(side="bottom", fill="x", expand=1)
        #used the tk instead of ttk library for this, allows font and color mods

            #Save Button
        self.saveButton = tk.Button(framered, text="Save Data", bg='green', font=('Arial',20,'bold'),
            command=self.saveData)
        self.saveButton.pack(side="left", padx=5, pady=5)

            #Log button
        self.logButton = tk.Button(framered, text="Start Data Logging", bg="blue", font=('Arial',20,'bold'),
            command=self.logData)
        self.logButton.pack(side="left", padx=5, pady=5)

            #Stop button
        self.stopButton = tk.Button(framered, text="Stop Motor", bg='red', font=('Arial',20,'bold'),
            command=self.stopMotor)
        self.stopButton.pack(side="right", padx=5, pady=5)
         

    #Button behavior functions (hopefully self-explanatory)
         
    def onClickAuto(self): #for the throttle sweep (should rename)
        pass #(I guess I can make it do something if I want)

    def MaxA(self):
        #self.MaxA_Entry.get()
        pass
            
    def MaxV(self):
        pass #not sure why these are even functions

    def onScaleThrottle(self, val):
        throttle = str(int(float(val)))
        self.throttlevar.set(throttle + "%")
        self.throttleval.set(throttle)
        try:
            self.SC.sendThrottleSetting(self.throttleval.get())
        except:
            self.textboxvar.set("Something went wrong, is serial connected?")

    def startSerial(self):
        COM_Port = self.selected_s_Port.get()
        #print type(COM_Port)
        #print COM_Port
        if "COM" in COM_Port:
            self.textboxvar.set("Starting Serial on port " + self.selected_s_Port.get())
            #serialThread = Thread(target=SerialComm, args=(COM_Port)) #probably want to pass the self.vars?
            #serialThread.start()
            #threads.append(serialThread)
            try:
                self.ser = serial.Serial(self.selected_s_Port.get(), 9600) #Baud rate = 9600
                self.SC = SerialComm(self.ser, 50) #Dict deques' maxlength = 50
                
                for key in self.SC.dict.keys(): #Initialize dict deques with values so no length errors -Austin
                    for i in range(self.SC.dict[key].maxlen):
                        self.SC.dict[key].append(None)
                
                self.serialStatus = True
            except Exception,e: #if the com port is wrong dont start serial
                print str(e)
                self.textboxvar.set("Error starting serial on port " + self.selected_s_Port.get() + ": " + str(e))
        else:
            self.textboxvar.set("Please select a port (current port: " + self.selected_s_Port.get() + ")")
            
            self.serialStatus = False

    def stopSerial(self):
        try:
            #serialThread.join()
            
            self.serialStatus = False
            self.SC = None #hopefully this works
            try:
                self.ser.close()
            except Exception, e:
                print str(e)
        except:
            pass

    def startMotor(self): #gonna have to make this send a serial message (maybe a popup to confirm too
        if self.autovar.get(): #I'll give you 5 seconds to move your fingers out of the way
            print "Preparing to sweep throttle range in 5 seconds"
            self.textboxvar.set("Sweeping throttle range in 5 seconds")
            self.startmotor.set(True)
            try:
                for throttle in range(0,100):
                    self.onScaleThrottle(throttle)
                    self.scale.set(throttle)
                    self.SC.sendPowerSetting(self.startmotor.get())
                    self.parent.after(0.1) #timestep
                self.parent.after(1) #wait for a second at the end
                self.onScaleThrottle(0)
                self.scale.set(0)
                self.stopMotor()
            except:
                self.textboxvar.set("Something went wrong, is serial connected?")
        else:
            print "starting motor at " + str(self.throttlevar.get()) + " percent"
            self.textboxvar.set("Starting motor at " + str(self.throttlevar.get()) + "% in 5 seconds")
            self.startmotor.set(True)
            try:
                #for some reason time.sleeps seem to hate windows
                self.parent.after(5)
                self.SC.sendPowerSetting(self.startmotor.get())
            except:
                self.textboxvar.set("Something went wrong, is serial connected?")

    def stopMotor(self):
        #stop motor
        print "Stopping motor"
        self.textboxvar.set("Stopping motor (not implemented yet)")
        self.startmotor.set(False)
        #self.throttlevar.set("0%") #not sure we want to reset the throttle value
        try:
            self.SC.sendPowerSetting(self.startmotor.get())
        except:
            self.textboxvar.set("Something went wrong, is serial connected?")

    def saveData(self):
        #save to csv
        self.textboxvar.set("Saving data?")
        try:
          self.loggedData
        except AttributeError:
            self.textboxvar.set("No recorded data.")
        else:
            if messagebox.askokcancel("Save", "This will overwrite any data.csv file in the directory. Save anyways?"):
                l = self.loggedData
                with open('data.csv', 'wb') as f:
                   wtr = csv.writer(f, delimiter= ',')
                   wtr.writerows( l )
                self.parent.after(2)
                self.textboxvar.set("Data saved!")

    def updateValues(self):
        #update motor values
        print "Updating motor values"
        self.textboxvar.set("Updating motor values")
        try:
            sendMaxCurrent(self.MaxA_Entry.get())
            sendMaxVoltage(self.MaxV_Entry.get())
        except:
            self.textboxvar.set("Something went wrong, is serial connected?")

    def logData(self):
        if self.logstate.get():
            self.logButton.configure(text = 'Start Data Logging')
            self.logButton.configure(bg = 'blue')
            self.logstate.set(False)
        else:
            self.logButton.configure(text = 'Stop Data Logging')
            self.logButton.configure(bg = 'orange')
            self.logstate.set(True)
            self.loggedData = []


if __name__ == '__main__':
    main()  
