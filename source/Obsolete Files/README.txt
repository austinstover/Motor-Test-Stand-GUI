UPDATE: Now probably works without python and all the scary stuff. Py2exe is amazing.

WARNING: Don't put your hands in the propeller when you run this, who knows what kind of bugs there may be.
	 I take no responsibility for cuts and any physical harm.

The data is output to "Data.csv", the software will warn you but be aware the file is overwritten when you save the data.

If you still want to run "control panel.py" directly:
Dependencies (if there are any more it should tell you in the error message):
-Python 2.7 (or any 2.x version is likely to work)
-matplotlib
-tkinter
-pySerial
-numpy

#Known Issues:
-Starting a second instance of the program may cause the program to crash (WILL NOT FIX)
-Scaling has issues, disabled maximizing the window (WILL NOT FIX)
-Force-killing the GUI will leave leftover threads running, this may bog down your computer, use the GUI button

Comments:

Hopefully someone can take care of the arduino side, I'm really not the best at it (though it compiled! IT COMPILED!!!).
Anyways don't lick the motor, don't put your fingers in moving parts and don't go too crazy with the sliders trying to break my
beautiful piece of software. 

May it be used for ever and ever.

-Christophe Foyer, co-founder of WUDBF and propulsion team god


Okay. First of all, I want to say: it's my software too, Christophe. To all those who are reading this and do not know, (My salutations 
for getting this far into the Readme) I wrote the SerialComm class and all of the Arduino stuff and spent hours and hours and hours 
debugging Christophe's spaghetti code (And it probably still has a bug or two hidden away somewhere). So the whole reason this 
program works, Christophe, is because of me. Okay!?

On a more serious note, the Arduino side was built and tested on an Arduino UNO (so far at least), but it should work on other Arduinos 
too. Hopefully. If you have any trouble with or want to modify the code for reading/sending messages on the Python side, I highly 
recommend carefully reading my SerialComm class documentation, (Please?) which is included in the SerialComm subdirectory, under
pythonDocs\html\index.html. It also lays out the protocol for sending messages on the Arduino side. And good luck.

Best Wishes,
Austin Stover, original member of WUDBF and 2017/2018 CAD lead



































































Why are you reading this?
Get back to work, you have some tests to run! D:<