#!/usr/bin/python
# -*-coding:utf-8-*

# Usage : python jap_segmenter.py
# Require : wapiti

from xml.dom.minidom import parse
import codecs
import os
import re

################################################################################
# Parameters
################################################################################
TRAINFILE = "./knbc-train.xml"
TESTFILE = "./knbc-test.xml"

WAPITITRAINFILE = "./wapiti-train.txt"
WAPITITESTFILE = "./wapiti-test.txt"
WAPITIMODELFILE = ".wapiti-model.txt"
WAPITIHYPFILE = "./wapiti-hyp.txt"

PATTERNFILE = "./pattern.txt"

OUTPUTFILE = "./output.xml"

CHARTYPEFILE = "./character-type.txt"
################################################################################



################################################################################
# Functions
################################################################################

################################################################################

# Creation of train file, which will be given to Wapiti
# Labels are :
# - F : First character of the word
# - M : Middle character of the word
# - L : Last character of the word
# - S : Single character word
# The character type (H-hiragana, K-katakana, O-other) is also added in the file
def createTrain(trainfile, wapititrainfile):
	dom = parse(trainfile)
	with codecs.open(wapititrainfile, 'w', 'utf-8') as train:
		for sentence in dom.getElementsByTagName('sentence'):
			#raw = sentence.getElementsByTagName('raw')[0].firstChild.wholeText
			for token in sentence.getElementsByTagName('token'):
				tok = token.firstChild.wholeText
				if len(tok) == 1:
					chartype = getCharType(tok,HIRAGANAS,KATAKANAS)
					train.write(tok+'\t'+chartype+'\tS\n')
				else:
					cpt = 1
					for car in tok:
						chartype = getCharType(car,HIRAGANAS,KATAKANAS)
						if cpt == 1:
							train.write(car+'\t'+chartype+'\tF\n')
						elif cpt == len(tok):
							train.write(car+'\t'+chartype+'\tL\n')
						else:
							train.write(car+'\t'+chartype+'\tM\n')
						cpt = cpt+1
			train.write('\n')


# Creation of test file, without labels
def createTest(testfile,wapititestfile):
	dom = parse(testfile)
	with codecs.open(wapititestfile, 'w', 'utf-8') as test:
		for sentence in dom.getElementsByTagName('sentence'):
			raw = sentence.getElementsByTagName('raw')[0].firstChild.wholeText
			for car in raw:
				chartype = getCharType(car,HIRAGANAS,KATAKANAS)
				test.write(car+'\t'+chartype+'\n')
			test.write('\n')


# Convert hyp file to xml output
def hypToXml(wapitihypfile,outputfile):
	with codecs.open(outputfile, "w", "utf-8") as output:
		output.write('<?xml version="1.0" encoding="UTF-8" ?>\n')
		output.write('<dataset>\n')
		sentences = []
		with codecs.open(wapitihypfile, "r", "utf-8") as hypfile:
			sentence = ""
			for line in hypfile:
				#print line, len(line)
				if len(line) == 1:
					sentences.append(sentence)
					sentence = ""
				else:
					matchObj = re.match( r'(.*)\t(.*)\t(.*)', line, re.M|re.I)
					car = matchObj.group(1)
					label = matchObj.group(3)
					if label == "S" or label == "L":
						sentence = sentence + car + " "
					else:
						sentence = sentence + car
		i = 0
		for sentence in sentences:
			output.write('\t<sentence sid="'+str(i)+'">\n')
		 	output.write('\t\t<raw>'+sentence[:-1]+'</raw>\n')
		 	output.write('\t</sentence>\n')
		 	i = i+1
		output.write('</dataset>')


# Get the list of all Hiraganas
def getHiraganas(filename):
	hiraganas = []
	with codecs.open(CHARTYPEFILE, 'r', 'utf-8') as charfile:
		for line in charfile:
			if 'Hiragana' in line:
				hiraganas.append(line.split('\t')[3])
	return hiraganas


# Get the list of all Katakanas
def getKatakanas(filename):
	katakanas = []
	with codecs.open(CHARTYPEFILE, 'r', 'utf-8') as charfile:
		for line in charfile:
			if 'Katakana' in line:
				katakanas.append(line.split('\t')[3])
	return katakanas


# Return the type of a character :
# - H : Hiragana
# - K : Katakana
# - O : Other
def getCharType(car,hiraganas,katakanas):
	chartype = 'O'
	if car in hiraganas:
		chartype = 'H'
	elif car in katakanas:
		chartype = 'K'
	return chartype

################################################################################



################################################################################
# Main
################################################################################

print 'Loading Hiraganas...'
HIRAGANAS = getHiraganas(CHARTYPEFILE)

print 'Loading Katakanas...'
KATAKANAS = getKatakanas(CHARTYPEFILE)

print 'Creating train file...'
createTrain(TRAINFILE,WAPITITRAINFILE)

print 'Creating test file...'
createTest(TESTFILE,WAPITITESTFILE)

# Train model with Wapiti
print 'Training with Wapiti...'
wapititrain = 'wapiti train -p '+PATTERNFILE+' '+WAPITITRAINFILE+' '+WAPITIMODELFILE
os.system(wapititrain)

# Label with our model
print 'Labeling...'
wapitilabel = 'wapiti label -m '+WAPITIMODELFILE+' -p '+WAPITITESTFILE+' '+WAPITIHYPFILE
os.system(wapitilabel)

print 'Converting to xml...'
hypToXml(WAPITIHYPFILE,OUTPUTFILE)

################################################################################