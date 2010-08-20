#!/usr/bin/env python2.4

import os, sys
from lxml import etree
from Tkinter import *
from notebook import *
import tkSimpleDialog, tkMessageBox

parser = etree.XMLParser(remove_blank_text=True)
doc = etree.parse("life.xml", parser)

relaxng = etree.RelaxNG(etree.parse("lifeplanner.rng"))
if not relaxng.validate(doc):
    print "Could not parse life:"
    print relaxng.error_log.last_error
    sys.exit(1)

class PlannerGUI:
    def __init__(self, master):

	nb = notebook(master, TOP)

	tcframe = Frame(nb())
	pframe = Frame(nb())

	nb.add_screen(tcframe, "Terms and Courses")
	nb.add_screen(pframe, "Academic Programs")

	menubar = Menu(master)
	filemenu = Menu(menubar, tearoff=0)
	filemenu.add_command(label="Open")
	filemenu.add_command(label="Save", command=self.save)
	filemenu.add_separator()
	filemenu.add_command(label="Exit", command=root.quit)
	menubar.add_cascade(label="File", menu=filemenu)
	master.config(menu=menubar)

	Label(tcframe,text="Terms:").grid(row=0, column=0, columnspan=3)
    
	self.termlistscroll = Scrollbar(tcframe, orient=VERTICAL)
	self.termlist = Listbox(tcframe, exportselection=0, 
				yscrollcommand=self.termlistscroll.set)
	self.termlistscroll.config(command=self.termlist.yview)

	self.termlistscroll.grid(row=1,column=2, sticky=N+S)
	self.termlist.grid(row=1, column=0, columnspan=2, sticky=N+S+E+W)
	
	self.termlist.bind('<Button-1>',lambda e: self.termlist.focus_set())

	self.refreshTerms()

	addt = Button(tcframe, text="Add Term", command=self.addTerm).grid(row=2, column=0)
	delt = Button(tcframe, text="Delete Term", command=self.delTerm).grid(row=2, column=1)


	Label(tcframe,text="Courses:").grid(row=0, column=4, columnspan=4)

	self.courselistscroll = Scrollbar(tcframe, orient=VERTICAL)
	self.courselist = Listbox(tcframe, exportselection=0,
				  yscrollcommand=self.courselistscroll.set)
	self.courselistscroll.config(command=self.courselist.yview)
	self.courselistscroll.grid(row=1, column=7, sticky=N+S)
	self.courselist.grid(row=1, column=4, columnspan=3, sticky=N+S+E+W)
	self.courselist.bind('<Button-1>',lambda e: self.courselist.focus_set())


	self.currentTerm = None

	def poll():
	    if self.termlist.curselection():
		now = self.termlist.get(self.termlist.curselection())
	    else:
		now = None
	    if now is None:
		self.courselist.delete(0, END)
	    elif now != self.currentTerm:
		self.currentTerm = now
		self.refreshCourses()
	    self.courselist.after(250, poll)

	poll()

	addc = Button(tcframe, text="Add Course", command=self.addCourse).grid(row=2, column=4)
	delc = Button(tcframe, text="Delete Course", command=self.delCourse).grid(row=2, column=5)
	editc = Button(tcframe, text="Edit Course", command=self.editCourse).grid(row=2, column=6)

	self.statusbar = Label(tcframe, text="", bd=1, relief=SUNKEN, anchor=W)
	self.statusbar.grid(row=3, column=0, columnspan=7, sticky=E+W)

	self.currentCourse = None

	def pollCourse():
	    if self.courselist.curselection():
		now = self.courselist.get(self.courselist.curselection())
	    else:
		now = None
	    if now is None:
		self.statusbar.config(text="")
	    elif now != self.currentTerm:
		self.currentCourse = now
		term = self.termlist.get(self.termlist.curselection())
		try:
		    self.statusbar.config(
			text=doc.xpath("//term[@date='"+term+
				       "']/course[@name='"+
				       self.currentCourse+"']/title/text()")[0])
		except:
		    self.statusbar.config(text="")
	    self.courselist.after(250, pollCourse)

	pollCourse()

    
    def refreshCourses(self):
	self.courselist.delete(0, END)
	for course in doc.xpath("//term[@date='"+self.currentTerm+"']/course"):
	    self.courselist.insert(END,course.attrib['name'])
	self.courselist.see(END)
		    
    def refreshTerms(self):
	self.termlist.delete(0, END)
	for term in doc.findall("term"):
	    date = term.attrib["date"]
	    self.termlist.insert(END, date)


    def addTerm(self):
	newterm = tkSimpleDialog.askinteger("Add Term", "Term start date")
	if newterm:
	    newterm = str(newterm)
	    if doc.xpath("//term[@date='"+newterm+"']"):
		tkMessageBox.showwarning("Add Term", "Term "+newterm+" already exists.")
		return
	    etree.SubElement(doc.getroot(),"term").set("date",newterm)
	    self.refreshTerms()

    def delTerm(self):
	if self.termlist.curselection():
	    t = self.termlist.get(self.termlist.curselection())
	    if tkMessageBox.askyesno("Delete term", "Are you sure you want to permanently delete term %s and all courses in this term?" % t):
		e = doc.xpath("//term[@date='"+t+"']")[0]
		doc.getroot().remove(e)
		self.refreshTerms()

    def addCourse(self):
	data={}
	data['term'] = self.termlist.get(self.termlist.curselection())
	d = self.editCourseDialog(root, data=data)
	self.refreshCourses()

    def editCourse(self):
	data = {}
	data['term'] = self.termlist.get(self.termlist.curselection())
	data['course'] = self.courselist.get(self.courselist.curselection())
	d = self.editCourseDialog(root, data=data)
	self.refreshCourses()
    
    def delCourse(self):
	term = self.termlist.get(self.termlist.curselection())
	course = self.courselist.get(self.courselist.curselection())

	if term and course and tkMessageBox.askyesno("Delete course", "Are you sure you want to permanently delete the course %s?" % course):
	    t = doc.xpath("//term[@date='"+term+"']")[0]
	    c = doc.xpath("//term[@date='"+term+
			       "']/course[@name='"+course+"']")[0]
	    t.remove(c)
	    self.refreshCourses()

    def save(self):
	doc.write("life_out.xml", pretty_print=True)

    class editCourseDialog(tkSimpleDialog.Dialog):

	def __init__(self, parent, title=None, data=None):
	    self.data = data
	    tkSimpleDialog.Dialog.__init__(self, parent, title)
	    

	def body(self, master):
	    Label(master, text="Course name:").grid(row=0, sticky=E, columnspan=2)
	    Label(master, text="Course title:").grid(row=1, sticky=E, columnspan=2)
	    Label(master, text="Credits:").grid(row=2, sticky=E, columnspan=2)
	    Label(master, text="Failed:").grid(row=3, sticky=E, columnspan=2)
	    
	    self.name = Entry(master)
	    self.name.grid(row=0, column=2, sticky=W)
	    self.title = Entry(master)
	    self.title.grid(row=1, column=2, sticky=W)
	    self.credits = Entry(master, width=3)
	    self.credits.grid(row=2, column=2, sticky=W)
	    self.fv = IntVar()
	    self.failed = Checkbutton(master, variable=self.fv)
	    self.failed.grid(row=3, column=2, sticky=W)

	    Label(master, text="Prerequisites:").grid(row=4,column=0)


	    self.plists = Scrollbar(master, orient=VERTICAL)
	    self.plist = Listbox(master, height=4, exportselection=0,
				 yscrollcommand=self.plists.set)
	    self.plists.config(command=self.plist.yview)
	    self.plists.grid(row=5, column=1, rowspan=3, sticky=N+S+W)
	    self.plist.grid(row=5, column=0, rowspan=3, sticky=N+S+E+W)
	    self.plist.bind('<Button-1>',lambda e: self.plist.focus_set())


	    self.addp = Button(master, text="Add prerequisite group",
			       command=self.addPrereq).grid(row=5, column=2)
	    self.editp = Button(master, text="Edit prerequisite group",
			       command=self.editPrereq).grid(row=6, column=2)
	    self.delp = Button(master, text="Delete prerequisite group",
			       command=self.delPrereq).grid(row=7, column=2)

	    Label(master, text="Corequisites:").grid(row=8,column=0)

	    self.clists = Scrollbar(master, orient=VERTICAL)
	    self.clist = Listbox(master, height=4,exportselection=0,
				 yscrollcommand=self.clists.set)
	    self.clists.config(command=self.clist.yview)
	    self.clists.grid(row=9, column=1, rowspan=2, sticky=N+S+W)
	    self.clist.grid(row=9, column=0, rowspan=2,  sticky=N+S+E+W)
	    self.clist.bind('<Button-1>',lambda e: self.clist.focus_set())

	    self.addc = Button(master, text="Add corequisite",
			       command=self.addCoreq).grid(row=9, column=2)
	    self.delc = Button(master, text="Delete corequisite",
			       command=self.delCoreq).grid(row=10, column=2)

	    self.pdata = {}

	    if "course" in self.data.keys():
		course = doc.xpath("//term[@date='"+self.data['term']+
				   "']/course[@name='"+self.data['course']+"']")[0]
		self.name.insert(0,course.attrib['name'])
		self.title.insert(0,course.find('title').text)
		self.credits.insert(0,course.attrib['credits'])
		if course.attrib.get('status',"") == "failed":
		    self.failed.select()
		for prereqSet in course.findall("prerequisite"):
		    count = prereqSet.attrib["count"] 
		    pl = []
		    for prereq in prereqSet.findall("name"):
			pl.append(prereq.text)
		    groupname = ", ".join(pl)
		    self.pdata[groupname] = (count, pl)
		    self.plist.insert(END, groupname)
		for coreq in course.findall("corequisite"):
		    self.clist.insert(END, coreq[0].text)


	def apply(self):
	    term = doc.xpath("//term[@date='"+self.data['term']+"']")[0]

	    if "course" in self.data.keys():
		course = doc.xpath("//term[@date='"+self.data['term']+
				   "']/course[@name='"+self.data['course']+"']")[0]
		term.remove(course)

	    course = etree.SubElement(term, "course")
	    course.set("name", self.name.get())
	    course.set("credits", self.credits.get())
	    title = etree.SubElement(course, "title")
	    title.text = self.title.get()
	    if self.fv.get():
		course.set("status", "failed")
	    
	    for prereqSet in self.pdata:
		pe = etree.SubElement(course, "prerequisite")
		pe.set("count", self.pdata[prereqSet][0])
		for cn in self.pdata[prereqSet][1]:
		    etree.SubElement(pe,"name").text = cn
	    
	    for coreq in self.clist.get(0, END):
		etree.SubElement(etree.SubElement(course, "corequisite"),"name").text = coreq

	def validate(self):
            if not self.title.get():
                tkMessageBox.showwarning("Course","The course title must be set.")
                return False
            if not self.name.get():
                tkMessageBox.showwarning("Course","The course name must be set.")
                return False
            try:
                c = int(self.credits.get())
            except:
                tkMessageBox.showwarning("Course","The number of credits must be an integer.")
                return False
            return True

	def addCoreq(self):
	    coreq = tkSimpleDialog.askstring("Add corequisite","Corequisite name")
	    if coreq:
		if coreq in self.clist.get(0,END):
		    tkMessageBox.showwarning("Add corequisite", "Corequisite "+coreq+" already exists.")
		elif coreq != '':
		    self.clist.insert(END, coreq)
	    
	def delCoreq(self):
	    t = self.clist.curselection()
	    if t and tkMessageBox.askyesno("Delete corequisite", "Are you sure you want to remove the corequisite '%s'?" % self.clist.get(t)):
		self.clist.delete(t)

	def addPrereq(self):
	    r = self.editPrereqDialog(self)
	    if r.result:
		self.plist.insert(END,r.result[0])
		self.pdata[r.result[0]] = (r.result[1],r.result[2])

	def delPrereq(self):
	    t = self.plist.curselection()
	    if t and tkMessageBox.askyesno("Delete prerequisite group", "Are you sure you want to remove the prerequisite '%s'?" % self.plist.get(t)):
		del self.pdata[self.plist.get(t)]
		self.plist.delete(t)

	def editPrereq(self):
	    t = self.plist.curselection()
	    r = self.editPrereqDialog(self, data=self.pdata[self.plist.get(t)])
	    if r.result:
		self.plist.delete(t)
		self.plist.insert(t,r.result[0])
		self.pdata[r.result[0]] = (r.result[1],r.result[2])

	class editPrereqDialog(tkSimpleDialog.Dialog):

	    def __init__(self, parent, title=None, data=None):
		self.data = data
		tkSimpleDialog.Dialog.__init__(self, parent, title)

	    def body(self, master):
		Label(master, text="Number of courses from group required:").grid(row=0)
		self.count = Entry(master, width=3)
		self.count.grid(row=0, column=1)
		
		self.plists = Scrollbar(master, orient=VERTICAL)
		self.plist = Listbox(master, height=4, exportselection=0,
				     yscrollcommand=self.plists.set)
		self.plists.config(command=self.plist.yview)
		self.plists.grid(row=1, column=1, rowspan=2, sticky=N+S+W)
		self.plist.grid(row=1, column=0, rowspan=2, sticky=N+S+E+W)
		self.plist.bind('<Button-1>',lambda e: self.plist.focus_set())
		
		self.addp = Button(master, text="Add prerequisite",
				   command=self.addPrereq)
		self.addp.grid(row=1, column=2)
		self.delp = Button(master, text="Delete prerequisite",
				   command=self.delPrereq)
		self.delp.grid(row=2, column=2)

		if self.data:
		    self.count.insert(0,self.data[0])
		    for course in self.data[1]:
			self.plist.insert(END,course)
		else:
		    self.count.insert(0,"1")


		return self.plist

	    def apply(self):		    
		self.result = (", ".join(self.plist.get(0, END)), self.count.get(),self.plist.get(0, END)) 

	    def validate(self):
		if not self.plist.get(0, END):
		    tkMessageBox.showwarning("Prerequisites","At least one prerequisite must be listed.")
		    return False
		try:
		    c = int(self.count.get())
		except:
		    tkMessageBox.showwarning("Prerequisites","The number of required courses must be an integer.")
		    return False
		if len(self.plist.get(0, END)) < int(self.count.get()):
		    tkMessageBox.showwarning("Prerequisites","The number of required courses must be fewer than the number of courses listed.")
		    return False
		return True

	    def addPrereq(self):
		prereq = tkSimpleDialog.askstring("Add prereqisite","Prerequisite name")
		if prereq:
		    if prereq in self.plist.get(0,END):
			tkMessageBox.showwarning("Add prerequisite", "Prerequisite "+prereq+" already exists.")
		    elif prereq != '':
			self.plist.insert(END, prereq)
	    
	    def delPrereq(self):
		t = self.plist.curselection()
		if t and tkMessageBox.askyesno("Delete prerequisite", "Are you sure you want to remove the prerequisite '%s'?" % self.plist.get(t)):
		    self.plist.delete(t)


root = Tk()

app = PlannerGUI(root)

root.mainloop()
