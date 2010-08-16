<?xml version="1.0" encoding="UTF-8" ?>

<xsl:stylesheet version="1.0" 
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
		xmlns="http://www.w3.org/1999/xhtml">
  <xsl:output method="text" />
  
  <xsl:template match="/">
    <xsl:text>
      digraph life {
      rankdir="LR" size="10,10" node [fontname="Helvetica Neue Light" fontsize=18]
    </xsl:text>
    <xsl:for-each select="//term">
      <xsl:for-each select="course">
	<xsl:variable name="courseNode">"<xsl:value-of select="@name" />.<xsl:value-of select="../@date"/>"</xsl:variable>
	<xsl:value-of select="$courseNode" /> [label="<xsl:value-of select="@name"/>" tooltip="<xsl:value-of select="title" />"  URL="#<xsl:value-of select="@name" />.<xsl:value-of select="../@date"/>"
	<xsl:if test="@inorder = 'n'  or @status = 'failed'">
	  <xsl:text> style="filled" fillcolor = "#ffff00"</xsl:text>
	</xsl:if>
	<xsl:if test="@used = 'y'">
	  <xsl:text> style="setlinewidth(4)"</xsl:text>
	</xsl:if>
	]
	<xsl:for-each select="prerequisite/name[@found='y']">
	  <xsl:variable name="c" select="." />
	  "<xsl:value-of select="$c" />.<xsl:value-of select="//term/course[@name=$c and not(@status='failed')]/../@date" />"-&gt;<xsl:value-of select="$courseNode" />
	  <xsl:text>
	    
	  </xsl:text>
	</xsl:for-each>
	<xsl:for-each select="corequisite[@satisfied = 'y' or @satisfied='p']/name">
	  <xsl:variable name="c" select="." />
	  "<xsl:value-of select="$c" />.<xsl:value-of select="//term/course[@name=$c and not(@status='failed')]/../@date" />"-&gt;<xsl:value-of select="$courseNode" /> [dir="both" arrowhead="empty" arrowtail="empty"]
	  <xsl:text>
	    
	  </xsl:text>
	</xsl:for-each>
      </xsl:for-each>
    </xsl:for-each>
    <xsl:for-each select="//term"><xsl:value-of select="@date" /><xsl:if test="following-sibling::term">-&gt;</xsl:if></xsl:for-each>
<xsl:for-each select="//term">
<xsl:text>{ rank=same;</xsl:text>
<xsl:value-of select="@date" /> [URL="#<xsl:value-of select="@date" />"];
<xsl:for-each select="course">"<xsl:value-of select="@name" />.<xsl:value-of select="../@date"/>";</xsl:for-each>
<xsl:text>
}
</xsl:text>
</xsl:for-each>
  <xsl:text>
    }
  </xsl:text>
  
  </xsl:template>
</xsl:stylesheet>