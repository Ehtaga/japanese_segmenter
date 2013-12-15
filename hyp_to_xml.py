#!/usr/bin/python
# -*-coding:utf-8-*

from xml.dom.minidom import parse
import codecs
import re

################################################################################
# Parameters
################################################################################
WAPITIHYPFILE = "./wapiti-hyp.txt"
OUTPUTFILE = "./output.xml"
################################################################################


with codecs.open(OUTPUTFILE, "w", "utf-8") as outputfile:
	outputfile.write('<?xml version="1.0" encoding="UTF-8" ?>\n')
	outputfile.write('<dataset>\n')
	sentences = []
	with codecs.open(WAPITIHYPFILE, "r", "utf-8") as hypfile:
		sentence = ""
		for line in hypfile:
			#print line, len(line)
			if len(line) == 1:
				sentences.append(sentence)
				sentence = ""
			else:
				matchObj = re.match( r'(.*)\t(.*)', line, re.M|re.I)
				car = matchObj.group(1)
				label = matchObj.group(2)
				if label == "S" or label == "L":
					sentence = sentence + car + " "
				else:
					sentence = sentence + car
	i = 0
	for sentence in sentences:
		outputfile.write('\t<sentence sid="'+str(i)+'">\n')
	 	outputfile.write('\t\t<raw>'+sentence[:-1]+'</raw>\n')
	 	outputfile.write('\t</sentence>\n')
	 	i = i+1
	outputfile.write('</dataset>')