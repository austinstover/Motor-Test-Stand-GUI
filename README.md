# Motor-Test-Stand-GUI

### Warning: This software is provided uncompiled to avoid issues regarding licensing and as such will require the dependencies listed below to run as intended. All libraries required are available for free through pip or online.

## Instructions:

Running the program is as easy as double-clicking the shortcut.

Connect the arduino using a USB cable and select the serial port in the software, then start the serial connection.

If the arduino is setup properly (arduino code uploaded to it), you should start seeing the output on the figures.

To start logging the data press the log data button.

To save the data click the save data button.
The data is output to "Data.csv", the software will warn you but be aware the file is overwritten when you save the data.

Stopping the motor can be done using the large "STOP MOTOR" button.
Running the motor can be done by pressing "start motor".
Changing the throttle slider will change the motor throttle setting.
You can also sweep the throttle range by checking the "sweep throttle" box.

WARNING: Don't put your hands in the propeller when you run this, who knows what kind of bugs there may be.
	 we take no responsibility for injuries, use at your own risk.


## Known Issues:
-Starting a second instance of the program may cause the program to crash (WILL NOT FIX)

-Scaling has issues, disabled maximizing the window (WILL NOT FIX)

-Force-killing the GUI will leave leftover threads running, this may bog down your computer, use the GUI button


## Compiling:

The source code is included.

To compile the code using py2exe, simply run compile.bat

## Dependencies (needed to compile):
-Python 2.7

-matplotlib

-tkinter

-pySerial

-numpy

-py2exe (for compiling to exe, optional)
