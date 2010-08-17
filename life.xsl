<?xml version="1.0" encoding="UTF-8" ?>

<xsl:stylesheet version="1.0" 
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
		xmlns="http://www.w3.org/1999/xhtml">
  <xsl:output method="xml" indent="yes"
	      doctype-public="-//W3C//DTD XHTML 1.0 Strict//EN" 
	      doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"/>
  
  <xsl:template match="/">
    <html xmlns="http://www.w3.org/1999/xhtml" xmlns:svg="http://www.w3.org/2000/svg" lang="en" xml:lang="en">
      <head>
	<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
	<title>Life</title>
	<style type="text/css">
	  td {border: 1px solid black; padding: 0.25em;}
	  table {border-collapse: collapse}
	  td ul {margin: 0; padding:0; margin-left: 1em;}
	</style>
      </head>
      <body>
	<a name="top" />
	<svg:svg id="life"/>
	<br /><br />
	<table>
	  <xsl:variable name="totalPossiblePoints">0</xsl:variable>
	  <xsl:variable name="totalEarnedPoints">0</xsl:variable>
	  <xsl:apply-templates select="//term"/>
<tr><td colspan="6"><xsl:value-of select="sum(//course/@credits)"/> credits attempted, <xsl:value-of select="sum(//course[not(@status='failed')]/@credits)"/> credits earned.</td></tr>
	</table>
	<xsl:apply-templates select="//program" />
      </body>
    </html>
  </xsl:template>
 
  <xsl:template match="term">
    <xsl:variable name="date" select="@date" />
    <tr><td colspan="6" style="text-align:center; font-weight:bold"><a name="{@date}"  />Term <xsl:value-of select="@date"/><br />
    <xsl:value-of select="sum(./*/@credits)"/> credit<xsl:if test = "sum(./*/@credits) > 1">s</xsl:if>, <xsl:value-of select="count(./course)"/> course<xsl:if test = "count(./course) > 1">s</xsl:if>
    <xsl:if test="@date &lt; $currentTerm and not(@type='transfer')">
      <br />
	<xsl:variable name="termEarnedPoints"><xsl:value-of select="sum(./*/@points)" /></xsl:variable>
	<xsl:variable name="termPossiblePoints"><xsl:value-of select="(sum(./*/@credits)*4)" /></xsl:variable>
	<xsl:variable name="totalEarnedPoints"><xsl:value-of select="sum(//course[../@date &lt;= $date and not(../@type='transfer')]/@points)" /></xsl:variable>
	<xsl:variable name="totalPossiblePoints"><xsl:value-of select="sum(//course[../@date &lt;= $date and not(../@type='transfer')]/@credits)*4" /></xsl:variable>
      <xsl:value-of select="substring(($termEarnedPoints div $termPossiblePoints)*4,1,4)" /> TGPA, <xsl:value-of select="substring( ($totalEarnedPoints div $totalPossiblePoints) *4,1,4)" /> CGPA
    </xsl:if>
</td></tr>
    <tr><td>Course number</td><td>Course name</td><td>Credits</td><td>Prerequisites</td><td>Corequisites</td><td>Remarks</td></tr>
    <xsl:apply-templates/>
    <tr><td colspan="6" style="text-align:center"><a href="#top">Return to top</a></td></tr>
  </xsl:template>
  
  <xsl:template match="course">
    <tr>
      <xsl:if test="@inorder = 'n'  or @status = 'failed'">
	<xsl:attribute name="bgcolor">#FFFF00</xsl:attribute>
      </xsl:if>
      <xsl:variable name="courseNode"><xsl:value-of select="@name" />.<xsl:value-of select="../@date"/></xsl:variable>
      
      <td><a name="{$courseNode}" /><xsl:value-of select="@name"/></td>
      <td><xsl:value-of select="title"/></td>
      <td><xsl:value-of select="@credits"/></td>
      <td>
	<xsl:choose>
	  <xsl:when test="count(prerequisite) = 0"><i>(none)</i></xsl:when>
	  <xsl:otherwise><xsl:apply-templates select="prerequisite"/></xsl:otherwise>
	</xsl:choose>
      </td>
      <td>
	<xsl:choose>
	  <xsl:when test="count(corequisite) = 0"><i>(none)</i></xsl:when>
	  <xsl:otherwise><xsl:apply-templates select="corequisite"/></xsl:otherwise>
	</xsl:choose>
      </td>
      <td><xsl:if test="@status ='failed'">Failed</xsl:if></td>
    </tr>
  </xsl:template>
  
  <xsl:template match="prerequisite">
      <xsl:if test="@count != count(./name)">
	<xsl:value-of select="@count" /> of the following <xsl:value-of select="count(./name)"/> courses<xsl:if test="@satisfied = 'n'">&#160;(this requirement not satisfied)</xsl:if>:
      </xsl:if>
      <ul>
	<xsl:for-each select="name">
	  <li>
	    <xsl:choose>
	      <xsl:when test="@found = 'n'"><xsl:value-of select="." /></xsl:when>
	      <xsl:otherwise>
		<xsl:variable name="c" select="." />
		<a><xsl:attribute name="href">#<xsl:value-of select="$c" />.<xsl:value-of select="//term/course[@name=$c and not(@status='failed')]/../@date" /></xsl:attribute><xsl:attribute name="title"><xsl:value-of select="//term/course[@name=$c and not(@status='failed')]/title" /></xsl:attribute><xsl:value-of select="$c" /></a></xsl:otherwise>
	    </xsl:choose>
	    <xsl:choose>
	      <xsl:when test="@found = 'n' and ../@satisfied='n'">&#160;(not found)</xsl:when>
	      <xsl:when test="@found = 'n'">&#160;(not found, but optional)</xsl:when>
	    </xsl:choose>
	  </li>
	</xsl:for-each>
      </ul>
  </xsl:template>

  <xsl:template match="corequisite">
      <ul>
	<xsl:for-each select="name">
	  <li>
	    <xsl:variable name="c" select="." />
	    <xsl:choose>
	      <xsl:when test="../@satisfied = 'n'"><xsl:value-of select="." />&#160;(not found)</xsl:when>
	      <xsl:when test="../@satisfied = 'p'">
		<xsl:variable name="destdate" select="//term/course[@name=$c and not(@status='failed')]/../@date" />
		<a><xsl:attribute name="href">#<xsl:value-of select="$c" />.<xsl:value-of select="//term/course[@name=$c and not(@status='failed')]/../@date" /></xsl:attribute><xsl:attribute name="title"><xsl:value-of select="//term/course[@name=$c and not(@status='failed')]/title" /></xsl:attribute><xsl:value-of select="$c" /></a>&#160;(found in term <a href="#{$destdate}"><xsl:value-of select="$destdate" /></a>)
	      </xsl:when>
	      <xsl:otherwise>
		<a><xsl:attribute name="href">#<xsl:value-of select="$c" />.<xsl:value-of select="//term/course[@name=$c and not(@status='failed')]/../@date" /></xsl:attribute><xsl:attribute name="title"><xsl:value-of select="//term/course[@name=$c and not(@status='failed')]/title" /></xsl:attribute><xsl:value-of select="$c" /></a>
	      </xsl:otherwise>
	    </xsl:choose>
	    <xsl:choose>
	      <xsl:when test="@found = 'n' and ../@satisfied='n'">&#160;(not found)</xsl:when>
	      <xsl:when test="@found = 'n'">&#160;(not found, but optional)</xsl:when>
	    </xsl:choose>
	  </li>
	</xsl:for-each>
      </ul>
  </xsl:template>
  
  
  <xsl:template match="program">
    <h1><xsl:value-of select="@name" /></h1>
    <xsl:if test="count(./required) > 0">
      <h2>Required Courses:</h2>
      <ul>
	<xsl:for-each select="required">
	  <li><xsl:value-of select="." /></li>
	</xsl:for-each>
      </ul>
    </xsl:if>
   
    <xsl:if test="count(./complementary) > 0">
      <h2>Complementary Courses:</h2>
      <xsl:for-each select="complementary">
	<div style="border: 1px solid black; float: left; margin: 1em; padding: 1em;">
	<xsl:if test="@count != count(./group)">
	  <xsl:value-of select="@count" /> of the following <xsl:value-of select="count(./group)"/> groups:<br />
	</xsl:if>
	<ol>
	  <xsl:for-each select="group">
	    <li>
	      <xsl:choose>
	      <xsl:when test="count(../group) > 1 "><xsl:value-of select="@name" /> (<xsl:value-of select="@credits" /> credits from the following list):</xsl:when>
	      <xsl:otherwise><xsl:value-of select="@credits" /> credits from the following list:</xsl:otherwise>
	      </xsl:choose>
	      <ul>
		<xsl:for-each select="name">
		  <li><xsl:value-of select="." /></li>
		</xsl:for-each>
		<xsl:for-each select="level">
		  <li><xsl:value-of select="." />00-level courses</li>
		</xsl:for-each>
	      </ul>
	    </li>
	  </xsl:for-each>
	  
	</ol>
	</div>
      </xsl:for-each>
    </xsl:if>
<hr style="clear:both;" />
  </xsl:template>
  
</xsl:stylesheet>
