import popen2
from StringIO import StringIO
from lxml import etree

class Planner:

    def __init__(self, doc):
	self.doc = doc

    def findCourse(self, name, term):
	c = doc.xpath("//course[not(@status='failed') and ../@date < "+term+" and @name='"+name+"']")
	if c:
	    return True
	else:
	    return False

    def findRequiredCourse(self, name):
	c = doc.xpath("//course[not(@status='failed') and @name='"+name+"']")
	if c:
	    return True
	else:
	    return False

    def findComplementaryLevel(self, level):
	c = doc.xpath("//course[not(@status='failed') and starts-with(@name,'"+level+"') and not(@used='y')]")
	if c:
	    return {"cc":c[0].attrib['credits'], "cn":c[0].attrib['name']}
	else:
	    return None


    def findComplementaryName(self, name):
	c = doc.xpath("//course[not(@status='failed') and @name='"+name+"' and not(@used='y')]")
	if c:
	    return {"cc":c[0].attrib['credits'], "cn":c[0].attrib['name']}
	else:
	    return False

    def markUsed(self, name):
	doc.xpath("//course[not(@status='failed') and @name='"+name+"']")[0].attrib['used'] = 'y'

    def checkPrerequisites(self):
	for term in self.doc.findall("term"):
	    date = term.attrib["date"]
	    for course in term.getchildren():
		course.attrib['inorder'] = "y"
		for prereqSet in course.findall("prerequisite"):
		    count = int(prereqSet.attrib["count"])
		    for prereq in prereqSet.findall("name"):
			if findCourse(prereq.text, date):
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

    def checkCorequisites(self):
	for term in self.doc.findall("term"):
	    date = term.attrib["date"]
	    for course in term.getchildren():
		for coreq in course.findall("corequisite"):
		    if doc.xpath("//course[not(@status='failed') and ../@date = "+date+" and @name='"+coreq[0].text+"']"):
			coreq.attrib['satisfied'] = "y"
		    elif doc.xpath("//course[not(@status='failed') and ../@date < "+date+" and @name='"+coreq[0].text+"']"):
			coreq.attrib['satisfied'] = "p"
			course.attrib['inorder'] = "n"
		    else:
			coreq.attrib['satisfied'] = "n"
			course.attrib['inorder'] = "n"
		    
    def checkPrograms():
	for program in self.doc.findall("program"):
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


    def render(self):

	dot_xslt = etree.XSLT(etree.parse("dot.xsl"))
	
	dotfile = str(dot_xslt(doc))

	dotproc = popen2.Popen3("/usr/local/graphviz-2.9/bin/dot -Tpng -olife.png -Tcmap", True)
	
	dotproc.tochild.write(dotfile)
	dotproc.tochild.close()
	
	fromdot = dotproc.fromchild.read()
	dotproc.fromchild.close()

	s = dotproc.wait()

	if os.WIFEXITED(s) and os.WEXITSTATUS(s) > 0:
	    #FIXME: handle errors gracefully
	    print "Problem with dot:"
	    print dotproc.childerr.read()
	    sys.exit(1)

	map = etree.parse(StringIO(fromdot), etree.HTMLParser())

	life_xslt = etree.XSLT(etree.parse("life.xsl"))

	life_html = life_xslt(doc)

	mapnode = life_html.xpath("//h:map[@name='life']",{'h':'http://www.w3.org/1999/xhtml'})[0]

	for e in map.findall("//area"):
	    mapnode.append(e)

	life_html.write("life.html", pretty_print=True)
