from Tkinter import *

 

root = Tk()

canvas = Canvas(root)

canvas.pack(side=TOP, expand=YES, fill=BOTH)

for i in range(1000):

            canvas.create_text(10, i*20, text="Hello world %d" % (i), anchor=NW)

 

def wheel(event):

            print "wheel"

            canvas.yview(SCROLL, -event.delta//120, UNITS)

 

canvas.focus_set()

canvas.bind('<MouseWheel>', wheel)

#canvas.bind('<4>', lambda e : canvas.yview(SCROLL, -1, UNITS))

#canvas.bind('<5>', lambda e : canvas.yview(SCROLL,  1, UNITS))

root.mainloop()

