#!/usr/bin/python
# -*- coding: utf-8 -*-

# Christophe Foyer 2017

# This piece of software is essentially duct-taped together, use at your own risk
# Also I'm making an effort to add comments, you can try and change it if you like.

#TODO: -Debug

### DEPENDENCIES ###
# - Tkinter        #
# - pySerial       #
# - MatPlotLib     #
# - numpy          #
####################



# Not all of this is being used, should clean up later (though no one ever does)
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

import numpy

from threading import Thread
from multiprocessing import Queue

import time
import sys
import glob

#import Austin's script
import SerialComm



class mSim(Frame): #could probably have renamed this class. Oh well...

  
    def __init__(self, parent):

        #base frame init
        Frame.__init__(self, parent)   
        self.parent = parent
        self.initUI()
        self.centerWindow()

        #Used to stop threads from infinitely looping
        global exitapp
        exitapp = False

        #serial port scanning thread (this is provided as-is and should work)
        def serial_ports():
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
            return result

        
        def scanLoop(): #This thread causes lag when closing the program, could fix, but eh it works
            while True and (not exitapp):
                self.s_Ports = serial_ports()
                #update every 4 seconds
                #(reducing this reduces lag on closing but increases the computation power required)
                #(Could create more elegant solution, but this works well enough)
                time.sleep(4)
                if exitapp == True:
                        break
        ###END FUNCTION###

        #Initiallize ports and start scanning thread
        self.s_Ports = []
        sScanThread = Thread(target=scanLoop, args=())
        sScanThread.start()
        threads.append(sScanThread)
        
        #create variables
        self.startmotor = BooleanVar()
        self.logstate = BooleanVar()
        self.throttlevar.set("0%") #ghetto fixes woo
        self.throttleval.set(0)

        #message sending thread
        def commsServer():
            self.sMsg = None
            #prev_sMsg = None #don't need this no more
            
            def sendSerial(msg, port, baudrate): #just a function to send serial messages
                if (port is not 'None'):
                    ser = serial.Serial(port, baudrate, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE)
                    if ser.isOpen():
                        ser.close()
                    ser.open()
                    for b in bytearray("message\n","UTF-8"):
                        ser.write(b)
                    ser.close()
            
            while True and (not exitapp):
                if self.sMsg != None:
                    msg = str(self.sMsg)
                    #send command over serial (pySerial)
                    sendSerial(msg, self.selected_s_Port, self.baudrate)
                    self.sMsg = None
                else:
                    time.sleep(0.1)
                if exitapp == True:
                        break
        ###END FUNCTION###

        #start the serial sending thingy
        commsServerThread = Thread(target=commsServer, args=())
        commsServerThread.start()
        threads.append(commsServerThread) #make sure you do this for any new thread you create!
        #failing to append threads to the threadlist is a criminal offense
        #not really but it'll stop them from being killed when the program closes

    def centerWindow(self):
      
        w = 800 #eh, who needs scaling anyways
        h = 640

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
        
        scale = Scale(frame1, from_=0, to=100, 
            command=self.onScaleThrottle)
        scale.pack(side=LEFT, padx=15)
        
        self.throttlevar = StringVar()
        self.throttleval = IntVar()
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
        drop = OptionMenu(frame1,self.selected_s_Port,"None",*self.s_Ports)
        drop.pack(side=LEFT, padx=5)

            #baudrate selection field (disabled)
##        drop2lbl = Label(frame1, text="Baudrate:", width=9)
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
        f = Figure(figsize=(4.5,4.5), dpi=100)
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

            #Refresh thread function
        def refreshFigure(): #this is threaded and just refreshes the figure (see time.sleep() for refresh rate)
            time.sleep(1)
            while True  and (not exitapp):
                self.a.clear()
                self.b.clear()
                self.c.clear()
                self.d.clear()
                if not serialStatus:
                    self.a.plot([1,2,3,4,5,6,7,8],[0,0,0,0,0,0,0,0])
                    self.b.plot([1,2,3,4,5,6,7,8],[0,0,0,0,0,0,0,0])
                    self.c.plot([1,2,3,4,5,6,7,8],[0,0,0,0,0,0,0,0])
                    self.d.plot([1,2,3,4,5,6,7,8],[0,0,0,0,0,0,0,0])
                else:
                    #debug plotsTimestamp
                    self.a.plot(serialData[-10:]["Timestamp"],serialData[-10:]["Timestamp"])
                    self.b.plot(serialData[-10:]["Timestamp"],serialData[-10:]["raw_temp"])
                    self.c.plot(serialData[-10:]["Timestamp"],serialData[-10:]["conv_temp"])
                    self.d.plot(serialData[-10:]["Timestamp"],serialData[-10:]["Potentiometer"])
                    #final plots
    ##                self.a.plot(serialData[-10:]["Timestamp"],serialData[-10:]["Thrust"])
    ##                self.b.plot(serialData[-10:]["Timestamp"],serialData[-10:]["RPM"])
    ##                self.c.plot(serialData[-10:]["Timestamp"],serialData[-10:]["Current"])
    ##                self.d.plot(serialData[-10:]["Timestamp"],serialData[-10:]["Voltage"])
                    #old demo stuff
    ##                self.a.plot([1,2,3,4,5,6,7,8],[5,6,1,3,self.throttleval.get(),9,3,5])
    ##                self.b.plot([1,2,3,4,5,6,7,8],[3,16,10,30,80,90,30,50])
    ##                self.c.plot([1,2,3,4,5,6,7,8],[8,5,4,(self.throttleval.get())**(0.5),15,15,15,20])
    ##                self.d.plot([1,2,3,4,5,6,7,8],[14,14,13,12,12,11.5,11.2,10.5])

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
                time.sleep(0.1) #refreshrate
        ###END FUNCTION###

            #Start the graphing thread
        plotThread = Thread(target=refreshFigure, args=())
        plotThread.start()
        threads.append(plotThread)
        
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
        pass #(I guess I can make it do something if I want)
    def MaxV(self):
        pass #(I guess I can make it do something if I want)

    def onScaleThrottle(self, val):
        throttle = str(int(float(val)))
        self.throttlevar.set(throttle + "%")
        self.throttleval.set(throttle)

    def startSerial(self):
        try:
            serialThread.join()
        except:
            pass
        COM_Port = self.selected_s_Port.get()
        #print type(COM_Port)
        #print COM_Port
        if "COM" in COM_Port:
            self.textboxvar.set("Starting Serial on port " + self.selected_s_Port.get())
            serialThread = Thread(target=SerialComm, args=(COM_Port)) #probably want to pass the self.vars?
            serialThread.start()
            threads.append(serialThread)
            global serialStatus
            serialStatus = True
        else:
            self.textboxvar.set("Please select a port (current port: " + self.selected_s_Port.get() + ")")
            global serialStatus
            serialStatus = False

    def stopSerial(self):
        try:
            serialThread.join()
            global serialStatus
            serialStatus = False
        except:
            pass

    def startMotor(self): #gonna have to make this send a serial message (maybe a popup to confirm too
        if self.autovar.get(): #I'll give you 5 seconds to move your fingers out of the way
            print "Preparing to sweep throttle range in 5 seconds"
            self.textboxvar.set("Sweeping throttle range in 5 seconds")
            self.startmotor.set(True)
        else:
            print "starting motor at " + str(self.throttlevar.get()) + " percent"
            self.textboxvar.set("Starting motor at " + str(self.throttlevar.get()) + "% in 5 seconds")
            self.startmotor.set(True)

    def runMotor(self):
        #runmotor at specified throttle
        self.textboxvar.set("Running the motor is not implemented yet")
        pass

    def stopMotor(self):
        #stop motor
        print "Stopping motor"
        self.textboxvar.set("Stopping motor (not implemented yet)")
        self.startmotor.set(False)
        #self.throttlevar.set("0%") #not sure we want to reset the throttle value
        pass

    def saveData(self):
        #save to csv
        self.textboxvar.set("Saving logged data.")
        #for some reason putting this in a thread causes it to not crash, welp
        try:
          self.loggedData
        except AttributeError:
            self.textboxvar.set("No recorded data.")
        else:
            if messagebox.askokcancel("Save", "This will overwrite any data.csv file in the directory. Save anyways?"):
                def saveCSV():
                    l = self.loggedData
                    with open('data.csv', 'wb') as f:
                       wtr = csv.writer(f, delimiter= ';')
                       wtr.writerows( l )
                    time.sleep(2)
                    self.textboxvar.set("Data saved!")
                saveThread = Thread(target=saveCSV, args=())
                saveThread.start()

    def updateValues(self):
        #update motor values
        print "Updating motor values"
        self.textboxvar.set("Updating motor values (WIP)")
        pass

    def logData(self):
        if self.logstate.get():
            self.logButton.configure(text = 'Start Data Logging')
            self.logButton.configure(bg = 'blue')
            self.logstate.set(False)
        else:
            self.logButton.configure(text = 'Stop Data Logging')
            self.logButton.configure(bg = 'orange')
            self.logstate.set(True)
            #start data logging (probably some kind of thread)
            def logSerialData():
                self.loggedData = []
                global serialData
                l=[serialData[-1].keys()]
                self.textboxvar.set("Logging from arduino is not implemented yet")
                #apparently spamming these messages causes crashes, good to know
                while self.logstate.get() and (not exitapp):
                    print 'Logging Data'
                    time.sleep(1)
                    global serialData
                    data = serialData[-1].values()
                    #recieve and store data (pySerial)
                    l.append(data)
                    self.loggedData = l
                    
            logThread = Thread(target=logSerialData, args=())
            logThread.start()
            threads.append(logThread)

def main():

    print "Initializing"
    print "Displaying GUI"

    global threads
    threads = []

    global serialData
    serialData = []
    
    global serialStatus
    serialStatus = False

    root = Tk()
    app = mSim(root)
    root.resizable(0,0) #This removes the maximize button (was causing issues)
    root.iconbitmap('favicon.ico') #favicon (so pretty)

    #Define closing behavior
    def on_closing():
        if messagebox.askokcancel("Quit", "Do you want to quit?"): #textbox on exit
            global exitapp #not sure this is still used, I'll leave it for now
            exitapp = True
            print " "
            print "Killing subprocesses"
            #Gotta make sure this doesn't take too long
            #Otherwise users might force-exit.
            #I guess I could make subprocesses check that the parent is still alive
            #Eh, too much work, maybe later. Just blame it on the user.
            time.sleep(1)
            #Join all the threads
            for t in threads:
                t.join()
            time.sleep(1)
            #kill the program
            root.destroy()

    #set closing behavior
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    #start GUI
    root.mainloop()  


if __name__ == '__main__':
    main()  
