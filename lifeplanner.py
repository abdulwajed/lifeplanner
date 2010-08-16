#!/usr/local/bin/python2.4

import os, sys, popen2, optparse, copy
from lxml import etree
from StringIO import StringIO

termtypes = {"00":"transfer",
	     "01":"winter",
	     "05":"summer",
	     "09":"fall"}

marks = {"A":4.0,
	 "A-":3.7,
	 "B+":3.3,
	 "B":3.0,
	 "B-":2.7,
	 "C+":2.3,
	 "C":2.0,
	 "D":1.0,
	 "F":0.0,
	 "KF":0.0,
	 "J":0.0,}

parser = etree.XMLParser(remove_blank_text=True)
lifeplan = etree.parse("life.xml", parser)
courses = etree.parse("courses.xml", parser)
programs = etree.parse("programs.xml", parser)

#relaxng = etree.RelaxNG(etree.parse("lifeplanner.rng"))
#if not relaxng.validate(doc):
#    print "Could not parse life:"
#    print relaxng.error_log.last_error
#    sys.exit(1)

def findCourse(name, term, type=""):
    print type
    #The prerequisite restrictions are relaxed for summer terms.
    #There are three summer sessions but they are represented as
    #one catalog term, so we assume that courses are taken in the right order
    #if a course and its prerequisites are taken during the same summer term.
    #Obviously this may not be the case, but there's no way to test for it.

    if type=="summer":
	return lifeplan.xpath("//course[not(@points=0) and ../@date <= "+term+" and @name='"+name+"']")
    else:
	return lifeplan.xpath("//course[not(@points=0) and ../@date < "+term+" and @name='"+name+"']")


def findRequiredCourse(name):
    return lifeplan.xpath("//course[not(@points=0) and @name='"+name+"']")

def findComplementaryLevel(level):
    c = lifeplan.xpath("//course[not(@points=0) and starts-with(@name,'"+level+"') and not(@used='y')]")
    if c:
	return {"cc":c[0].attrib['credits'], "cn":c[0].attrib['name']}
    else:
	return None

def findComplementaryName(name):
    c = lifeplan.xpath("//course[not(@status='failed') and @name='"+name+"' and not(@used='y')]")
    if c:
	return {"cc":c[0].attrib['credits'], "cn":c[0].attrib['name']}
    else:
	return False

def markUsed(name):
    lifeplan.xpath("//course[not(@status='failed') and @name='"+name+"']")[0].attrib['used'] = 'y'

def fixTermDateType(term):
    date = term.attrib["date"]
    if not term.attrib.get("type"):
	month = date[4:6]
	term.attrib["type"] = termtypes.get(month,"")
    type = term.attrib["type"]
    return (date, type)

def fixCourseMarks(course):
    if course.attrib.get("mark"):
	if marks.get(course.attrib['mark']) and marks[course.attrib['mark']] > 0:
	    course.attrib['points'] = str(int(course.attrib['credits']) * marks[course.attrib['mark']])
	else:
	    course.attrib['points'] = "0"
	    course.attrib['status'] = "failed"

	
def getCourseData(course):
    cdata = courses.xpath('//course[@name="'+course.attrib['name']+'"]')
    if cdata:
	cdata = copy.deepcopy(cdata[0])
	if course.attrib.get("mark"):
	    cdata.attrib['mark'] = course.attrib['mark']
	term.remove(course)
	term.append(cdata)
	print courses.xpath('//course[@name="'+course.attrib['name']+'"]')
    else:
	print course.attrib['name']


for program in lifeplan.findall("program"):
    pdata = 

for term in lifeplan.findall("term"):
    date, type = fixTermDateType(term)

    for course in term.getchildren():
	getCourseData(course)

    for course in term.getchildren():
	fixCourseMarks(course)

for term in lifeplan.findall("term"):
    #Don't process prerequisites and corequisites for transfer credits.
    #They're only in the data file so they can be used for calculating
    #credits and prerequisites for courses being taken now; it doesn't
    #matter if the prerequisites wouldn't be satisfied if the course
    #were taken for credit now.
    if type == "transfer":
	continue

    for course in term.getchildren():
	course.attrib['inorder'] = "y"

	#Now we get to do the prereqs dance!
	for prereqSet in course.findall("prerequisite"):
	    count = int(prereqSet.attrib["count"])
	    for prereq in prereqSet.findall("name"):
		    if findCourse(prereq.text, date, type):
			prereq.attrib['found'] = 'y'
			count -= 1
		    else:
			prereq.attrib['found'] = 'n'
		    
	    if count > 0:
		print "Missing prerequisite "+prereq.text+" for "+course.attrib["name"]
		course.attrib['inorder'] = "n"
		prereqSet.attrib['satisfied'] = "n"
	    else:
		prereqSet.attrib['satisfied'] = "y"

	for coreq in course.findall("corequisite"):
	    if lifeplan.xpath("//course[not(@status='failed') and ../@date = "+date+" and @name='"+coreq[0].text+"']"):
		coreq.attrib['satisfied'] = "y"
	    elif lifeplan.xpath("//course[not(@status='failed') and ../@date < "+date+" and @name='"+coreq[0].text+"']"):
		coreq.attrib['satisfied'] = "p"
		course.attrib['inorder'] = "n"

	    else:
		coreq.attrib['satisfied'] = "n"
		course.attrib['inorder'] = "n"
		    
def checkPrograms():
    for program in programs.findall("program"):
	print "\nEvaluating program \""+program.attrib["name"]+"\":"
	requiredCourses = program.findall("required")
	
	for course in requiredCourses:
	    name = course.text
	    if findRequiredCourse(name):
		print "\tFound required course: "+name
		markUsed(name)
	    else:
		print "\tDid not find required course: "+name

	complementaries =  program.findall("complementary")
	for complementary in complementaries:
	    count = int(complementary.attrib["count"])
	    for group in complementary.findall("group"):
		credits = int(group.attrib["credits"])
		notFound = []
		usedForGroup = []
		for node in group.getchildren():
		    if credits > 0:
			if node.tag == "level":
			    data = True
			    while credits > 0 and data is not None:
				data = findComplementaryLevel(node.text)
				if data:
				    credits -= int(data["cc"])
				    markUsed(data["cn"])
				    usedForGroup.append(data["cn"])
				else:
				    notFound.append(node.text+"00-level")
			elif node.tag == "name":
			    data = findComplementaryName(node.text)
			    if data:
				credits -= int(data["cc"])
				markUsed(data["cn"])
				usedForGroup.append(data["cn"])
			    else:
				notFound.append(node.text)
		if credits > 0:
		    print "\tNeed "+str(credits)+" credits from "+(", ".join(notFound))+" for "+group.attrib["name"]
		else:
		    count -= 1
		    print "\t"+group.attrib["name"]+" satisfied by "+(", ".join(usedForGroup))+"."
	    if count > 0:
		print "\tProgram not satisfied; need "+str(count)+" of the above groups"
	    else:
		print "\tProgram complementaries satisfied."

#credits = 0
#terms = courses.keys()
#terms.sort()
#for term in terms:
#    print '\nTerm '+term
#    tc = 0
#    for course in courses[term]:
#	print courses[term][course]
#	credits += int(courses[term][course].credits)
#	tc += int(courses[term][course].credits)

#    print str(tc) + " credits for term"

#print str(credits) + " credits total"

checkPrograms()

dot_xslt = etree.XSLT(etree.parse("dot.xsl"))

dotfile = str(dot_xslt(lifeplan))

dotproc = popen2.Popen3("/usr/local/graphviz-2.9/bin/dot -Tpng -olife.png -Tcmap", True)

dotproc.tochild.write(dotfile)
dotproc.tochild.close()

fromdot = dotproc.fromchild.read()
dotproc.fromchild.close()

s = dotproc.wait()

if os.WIFEXITED(s) and os.WEXITSTATUS(s) > 0:
    print "Problem with dot:"
    print dotproc.childerr.read()
    sys.exit(1)

map = etree.parse(StringIO(fromdot), etree.HTMLParser())

life_xslt = etree.XSLT(etree.parse("life.xsl"))

life_html = life_xslt(lifeplan, currentTerm="200701")

mapnode = life_html.xpath("//h:map[@name='life']",{'h':'http://www.w3.org/1999/xhtml'})[0]

for e in map.findall("//area"):
    mapnode.append(e)

life_html.write("life.html", pretty_print=True)
